"""
API服务器模块
提供RESTful API接口，用于网页内容爬取
"""

from typing import Dict, Any, List, Optional
import logging
import time
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# 导入配置
from config import (
    API_HOST, 
    API_PORT, 
    API_DEBUG, 
    DEFAULT_BROWSER, 
    HEADLESS_MODE
)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 导入WebCrawler类
from crawler import WebCrawler

# 全局爬虫实例池
crawler_pool = {}

@app.route("/", methods=["GET"])
def index() -> Response:
    """API服务器根路径处理器"""
    return jsonify({
        "name": "Selenium Web Crawler API",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api/extract", "method": "POST", "description": "提取URL内容"},
            {"path": "/api/extract-text", "method": "POST", "description": "提取URL文本内容"},
            {"path": "/api/batch", "method": "POST", "description": "批量提取多个URL内容"},
            {"path": "/api/status", "method": "GET", "description": "获取API服务器状态"}
        ]
    })

@app.route("/api/status", methods=["GET"])
def get_status() -> Response:
    """获取API服务器状态"""
    return jsonify({
        "status": "running",
        "active_crawlers": len(crawler_pool),
        "uptime": time.time() - app.start_time if hasattr(app, 'start_time') else 0
    })

@app.route("/api/extract", methods=["POST"])
def extract_content() -> Response:
    """
    提取URL内容的API端点
    
    此端点接收包含URL和选项的POST请求，使用Selenium WebDriver爬取指定网页的内容，
    并返回结构化的数据。
    
    请求体格式:
    {
        "url": "https://example.com",  # 必需，要爬取的网页URL
        "options": {                   # 可选，爬取选项
            "browser": "chrome",       # 可选，浏览器类型：chrome或firefox
            "headless": true,          # 可选，是否使用无头模式
            "handle_pagination": true  # 可选，是否处理分页内容
        }
    }
    
    成功响应:
    {
        "status": "success",           # 状态标识
        "url": "https://example.com",  # 请求的URL
        "title": "页面标题",            # 提取的页面标题
        "content": "页面内容..."        # 提取的HTML内容
    }
    
    错误响应:
    {
        "status": "error",            # 状态标识
        "message": "错误描述"          # 错误详情
    }
    
    Returns:
        Response: 包含提取内容或错误信息的JSON响应
    """
    crawler = None
    try:
        # 解析请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "无效的请求数据，需要JSON格式"
            }), 400
        
        # 获取URL
        url = data.get("url")
        if not url or not isinstance(url, str):
            return jsonify({
                "status": "error",
                "message": "请求中未提供有效的URL"
            }), 400
        
        # 获取选项
        options = data.get("options", {})
        browser_type = options.get("browser", DEFAULT_BROWSER)
        headless = options.get("headless", HEADLESS_MODE)
        handle_pagination = options.get("handle_pagination", True)
        
        # 创建爬虫实例
        crawler = WebCrawler()
        
        # 设置爬虫
        crawler.setup(
            browser_type=browser_type,
            headless=headless
        )
        
        # 执行爬取
        results = crawler.crawl_urls([url], handle_pagination=handle_pagination)
        
        if results and len(results) > 0:
            result = results[0]
            return jsonify({
                "status": "success",
                "url": url,
                "title": result.get("title", ""),
                "content": result.get("content", "")
            })
        else:
            return jsonify({
                "status": "error",
                "message": "未能提取到页面内容"
            }), 404
            
    except Exception as e:
        logger.exception(f"提取内容时发生异常: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"服务器内部错误: {str(e)}"
        }), 500
    finally:
        # 清理资源
        if crawler:
            crawler.cleanup()

@app.route("/api/extract-text", methods=["POST"])
def extract_text_content() -> Response:
    """
    提取URL文本内容的API端点
    
    此端点接收包含URL和选项的POST请求，使用Selenium WebDriver爬取指定网页的文本内容，
    并返回结构化的数据。
    
    请求体格式:
    {
        "url": "https://example.com",  # 必需，要爬取的网页URL
        "selector": "body",            # 可选，CSS选择器，用于定位要提取内容的元素
        "options": {                   # 可选，爬取选项
            "browser": "chrome",       # 可选，浏览器类型：chrome或firefox
            "headless": true           # 可选，是否使用无头模式
        }
    }
    
    Returns:
        Response: 包含提取文本内容或错误信息的JSON响应
    """
    crawler = None
    try:
        # 解析请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "无效的请求数据，需要JSON格式"
            }), 400
        
        # 获取URL
        url = data.get("url")
        if not url or not isinstance(url, str):
            return jsonify({
                "status": "error",
                "message": "请求中未提供有效的URL"
            }), 400
        
        # 获取选择器
        selector = data.get("selector", "body")
        
        # 获取选项
        options = data.get("options", {})
        browser_type = options.get("browser", DEFAULT_BROWSER)
        headless = options.get("headless", HEADLESS_MODE)
        
        # 创建爬虫实例
        crawler = WebCrawler()
        
        # 设置爬虫
        crawler.setup(
            browser_type=browser_type,
            headless=headless
        )
        
        # 访问页面
        results = crawler.crawl_urls([url])
        
        if not results or len(results) == 0:
            return jsonify({
                "status": "error",
                "message": "未能访问页面"
            }), 404
        
        # 提取文本内容
        text_content = crawler.extract_text_content(selector)
        
        return jsonify({
            "status": "success",
            "url": url,
            "title": results[0].get("title", ""),
            "text_content": text_content
        })
            
    except Exception as e:
        logger.exception(f"提取文本内容时发生异常: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"服务器内部错误: {str(e)}"
        }), 500
    finally:
        # 清理资源
        if crawler:
            crawler.cleanup()

@app.route("/api/batch", methods=["POST"])
def batch_extract() -> Response:
    """
    批量提取多个URL内容的API端点
    
    此端点接收包含多个URL和选项的POST请求，使用Selenium WebDriver爬取指定网页的内容，
    并返回结构化的数据。
    
    请求体格式:
    {
        "urls": ["https://example.com", "https://example.org"],  # 必需，要爬取的URL列表
        "options": {                   # 可选，爬取选项
            "browser": "chrome",       # 可选，浏览器类型：chrome或firefox
            "headless": true,          # 可选，是否使用无头模式
            "handle_pagination": true  # 可选，是否处理分页内容
        }
    }
    
    Returns:
        Response: 包含提取内容或错误信息的JSON响应
    """
    crawler = None
    try:
        # 解析请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "无效的请求数据，需要JSON格式"
            }), 400
        
        # 获取URL列表
        urls = data.get("urls")
        if not urls or not isinstance(urls, list) or len(urls) == 0:
            return jsonify({
                "status": "error",
                "message": "请求中未提供有效的URL列表"
            }), 400
        
        # 获取选项
        options = data.get("options", {})
        browser_type = options.get("browser", DEFAULT_BROWSER)
        headless = options.get("headless", HEADLESS_MODE)
        handle_pagination = options.get("handle_pagination", True)
        
        # 创建爬虫实例
        crawler = WebCrawler()
        
        # 设置爬虫
        crawler.setup(
            browser_type=browser_type,
            headless=headless
        )
        
        # 执行爬取
        results = crawler.crawl_urls(urls, handle_pagination=handle_pagination)
        
        return jsonify({
            "status": "success",
            "count": len(results),
            "results": results
        })
            
    except Exception as e:
        logger.exception(f"批量提取内容时发生异常: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"服务器内部错误: {str(e)}"
        }), 500
    finally:
        # 清理资源
        if crawler:
            crawler.cleanup()

def start_api_server(host=API_HOST, port=API_PORT, debug=API_DEBUG):
    """
    启动API服务器
    
    Args:
        host: 服务器主机地址
        port: 服务器端口
        debug: 是否启用调试模式
    """
    logger.info(f"启动API服务器 - 监听 {host}:{port}")
    app.start_time = time.time()
    app.run(host=host, port=port, debug=debug)