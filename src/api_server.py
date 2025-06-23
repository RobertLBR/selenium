"""
API服务器模块
提供HTTP接口，允许通过POST请求触发爬取操作
"""

import os
import json
import time
import threading
from typing import Dict, Any, List, Optional, Union
from flask import Flask, request, jsonify
from flask_cors import CORS

import config
from utils import get_logger, setup_logging, CrawlerException
from main import WebCrawler

# 设置日志
setup_logging()
logger = get_logger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域资源共享

# 存储爬取任务的状态
tasks = {}
task_lock = threading.Lock()
next_task_id = 1

class TaskStatus:
    """任务状态常量"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

def get_next_task_id() -> int:
    """获取下一个任务ID"""
    global next_task_id
    with task_lock:
        task_id = next_task_id
        next_task_id += 1
    return task_id

def update_task_status(task_id: int, status: str, result: Optional[Dict[str, Any]] = None,
                      error: Optional[str] = None) -> None:
    """
    更新任务状态
    
    Args:
        task_id: 任务ID
        status: 新状态
        result: 任务结果（可选）
        error: 错误信息（可选）
    """
    with task_lock:
        if task_id in tasks:
            tasks[task_id]["status"] = status
            tasks[task_id]["updated_at"] = time.time()
            
            if result is not None:
                tasks[task_id]["result"] = result
                
            if error is not None:
                tasks[task_id]["error"] = error

def crawl_task(task_id: int, urls: List[str], options: Dict[str, Any]) -> None:
    """
    执行爬取任务的线程函数
    
    Args:
        task_id: 任务ID
        urls: 要爬取的URL列表
        options: 爬取选项
    """
    crawler = None
    try:
        # 更新任务状态为运行中
        update_task_status(task_id, TaskStatus.RUNNING)
        
        # 创建爬虫实例
        crawler = WebCrawler()
        
        # 设置爬虫
        crawler.setup(
            browser_type=options.get("browser", config.DEFAULT_BROWSER),
            headless=options.get("headless", config.HEADLESS_MODE)
        )
        
        # 存储爬取结果
        results = {}
        
        # 爬取每个URL
        for url in urls:
            try:
                # 执行爬取
                if options.get("handle_pagination", True):
                    # 处理分页内容
                    pages_data = []
                    for page_data in crawler.page_scraper.scrape_with_pagination(url):
                        pages_data.append(page_data)
                    
                    # 合并分页数据
                    if pages_data:
                        merged_data = crawler.data_processor.merge_paginated_data(pages_data)
                        # 保存数据
                        saved_files = crawler.data_processor.save_data(merged_data)
                        results[url] = {
                            "status": "success",
                            "files": saved_files,
                            "page_count": len(pages_data)
                        }
                else:
                    # 爬取单页内容
                    page_data = crawler.page_scraper.scrape_page(url)
                    # 保存数据
                    saved_files = crawler.data_processor.save_data(page_data)
                    results[url] = {
                        "status": "success",
                        "files": saved_files,
                        "page_count": 1
                    }
            except Exception as e:
                logger.error(f"爬取URL失败: {url}, 错误: {str(e)}")
                results[url] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        # 更新任务状态为完成
        update_task_status(task_id, TaskStatus.COMPLETED, result=results)
        
    except Exception as e:
        logger.error(f"任务执行失败: {str(e)}")
        update_task_status(task_id, TaskStatus.FAILED, error=str(e))
    finally:
        # 清理资源
        if crawler:
            crawler.cleanup()

@app.route("/api/crawl", methods=["POST"])
def api_crawl() -> Dict[str, Any]:
    """
    爬取URL的API端点
    
    请求体格式:
    {
        "urls": ["https://example.com", ...],
        "options": {
            "browser": "chrome",
            "headless": true,
            "handle_pagination": true
        }
    }
    
    Returns:
        Dict[str, Any]: 包含任务ID的JSON响应
    """
    try:
        # 解析请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "无效的请求数据，需要JSON格式"
            }), 400
        
        # 验证URLs
        urls = data.get("urls")
        if not urls:
            # 尝试从单个url参数获取
            url = data.get("url")
            if url:
                urls = [url]
            else:
                return jsonify({
                    "status": "error",
                    "message": "请求中未提供URL"
                }), 400
        
        if isinstance(urls, str):
            urls = [urls]
            
        if not isinstance(urls, list):
            return jsonify({
                "status": "error",
                "message": "URLs必须是字符串或字符串列表"
            }), 400
        
        # 获取选项
        options = data.get("options", {})
        
        # 创建新任务
        task_id = get_next_task_id()
        tasks[task_id] = {
            "id": task_id,
            "urls": urls,
            "options": options,
            "status": TaskStatus.PENDING,
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # 启动爬取线程
        thread = threading.Thread(
            target=crawl_task,
            args=(task_id, urls, options)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "success",
            "message": "爬取任务已创建",
            "task_id": task_id
        })
        
    except Exception as e:
        logger.error(f"处理爬取请求时出错: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"处理请求时出错: {str(e)}"
        }), 500

@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task_status(task_id: int) -> Dict[str, Any]:
    """
    获取任务状态的API端点
    
    Args:
        task_id: 任务ID
        
    Returns:
        Dict[str, Any]: 包含任务状态的JSON响应
    """
    with task_lock:
        if task_id not in tasks:
            return jsonify({
                "status": "error",
                "message": f"任务ID {task_id} 不存在"
            }), 404
        
        task = tasks[task_id].copy()
        
    return jsonify({
        "status": "success",
        "task": task
    })

@app.route("/api/tasks", methods=["GET"])
def list_tasks() -> Dict[str, Any]:
    """
    列出所有任务的API端点
    
    Returns:
        Dict[str, Any]: 包含任务列表的JSON响应
    """
    with task_lock:
        task_list = list(tasks.values())
    
    return jsonify({
        "status": "success",
        "tasks": task_list
    })

def start_api_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """
    启动API服务器
    
    Args:
        host: 监听的主机地址
        port: 监听的端口
        debug: 是否启用调试模式
    """
    logger.info(f"API服务器正在启动，监听 {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    start_api_server()