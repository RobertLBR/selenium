"""
API服务器模块
提供HTTP接口，允许通过POST请求直接获取网页文本内容

API文档
-------

基础信息:
- 基础URL: http://localhost:5000
- 支持的请求方法: POST
- 响应格式: JSON
- 编码方式: UTF-8
- 跨域支持: 是

可用端点
--------

1. /api/extract
   用于提取网页内容的主要端点

   请求格式:
   ```json
   {
       "url": "https://example.com",
       "options": {
           "browser": "chrome",    // 可选，浏览器类型：chrome或firefox，默认为chrome
           "headless": true,       // 可选，是否使用无头模式，默认为true
           "handle_pagination": true // 可选，是否处理分页，默认为true
       }
   }
   ```

   成功响应格式:
   ```json
   {
       "status": "success",
       "url": "https://example.com",
       "title": "页面标题",
       "content": "提取的文本内容",
       "metadata": {
           "author": "作者名称",
           "date": "发布日期",
           "category": "分类",
           // ... 其他元数据
       },
       "page_count": 1  // 处理的页面数量
   }
   ```

   错误响应格式:
   ```json
   {
       "status": "error",
       "message": "错误描述"
   }
   ```

   状态码说明:
   - 200: 请求成功
   - 400: 请求参数错误（无效的URL或JSON格式）
   - 404: 未找到内容
   - 500: 服务器内部错误

调用示例
-------

使用curl:
```bash
curl -X POST http://localhost:5000/api/extract \
     -H "Content-Type: application/json" \
     -d '{
         "url": "https://example.com",
         "options": {
             "browser": "chrome",
             "headless": true,
             "handle_pagination": true
         }
     }'
```

使用Python requests:
```python
import requests

response = requests.post(
    'http://localhost:5000/api/extract',
    json={
        'url': 'https://example.com',
        'options': {
            'browser': 'chrome',
            'headless': True,
            'handle_pagination': True
        }
    }
)
data = response.json()
```

错误处理
-------
1. 请求错误
   - 无效的URL格式
   - 缺少必需的URL参数
   - 无效的JSON格式

2. 内容提取错误
   - 页面无法访问
   - 内容提取失败
   - 分页处理错误

3. 服务器错误
   - 浏览器启动失败
   - 资源清理错误
   - 其他内部错误

注意事项
-------
1. 建议在生产环境中启用HTTPS
2. 对于大型网页或多页内容，请求可能需要较长时间
3. 某些网站可能有反爬虫机制，可能需要适当的延迟和请求头
4. 确保有足够的系统资源（内存和CPU）来运行浏览器实例
"""

from typing import Dict, Any
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

@app.route("/api/extract", methods=["POST"])
def extract_content() -> Dict[str, Any]:
    """
    提取URL内容的API端点
    
    此端点接收包含URL和选项的POST请求，使用Selenium WebDriver爬取指定网页的内容，
    并返回结构化的数据。支持分页内容的自动处理。
    
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
        "content": "页面内容...",       # 提取的文本内容
        "metadata": {                  # 提取的元数据
            "author": "作者",
            "date": "2023-01-01",
            "category": "分类"
            // 其他可能的元数据
        },
        "page_count": 1               # 处理的页面数量
    }
    
    错误响应:
    {
        "status": "error",            # 状态标识
        "message": "错误描述"          # 错误详情
    }
    
    状态码:
    - 200: 请求成功
    - 400: 请求参数错误
    - 404: 未找到内容
    - 500: 服务器内部错误
    
    Returns:
        Dict[str, Any]: 包含提取内容或错误信息的JSON响应
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
        
        # 创建爬虫实例
        crawler = WebCrawler()
        
        # 设置爬虫
        crawler.setup(
            browser_type=options.get("browser", config.DEFAULT_BROWSER),
            headless=options.get("headless", config.HEADLESS_MODE)
        )
        
        # 执行爬取
        if options.get("handle_pagination", True):
            # 处理分页内容
            pages_data = []
            for page_data in crawler.page_scraper.scrape_with_pagination(url):
                pages_data.append(page_data)
            
            # 合并分页数据
            if pages_data:
                merged_data = crawler.data_processor.merge_paginated_data(pages_data)
                return jsonify({
                    "status": "success",
                    "url": url,
                    "title": merged_data.get("title", ""),
                    "content": merged_data.get("content", ""),
                    "metadata": merged_data.get("metadata", {}),
                    "page_count": len(pages_data)
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "未能提取到页面内容"
                }), 404
        else:
            # 爬取单页内容
            page_data = crawler.page_scraper.scrape_page(url)
            return jsonify({
                "status": "success",
                "url": url,
                "title": page_data.get("title", ""),
                "content": page_data.get("content", ""),
                "metadata": page_data.get("metadata", {}),
                "page_count": 1
            })
        
    except Exception as e:
        logger.error(f"提取内容失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"提取内容失败: {str(e)}"
        }), 500
    finally:
        # 清理资源
        if crawler:
            crawler.cleanup()

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