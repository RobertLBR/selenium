"""
Selenium Web Crawler 基本用法示例
"""

import os
import sys
import json
import requests
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crawler import WebCrawler
from src.config import DEFAULT_BROWSER, HEADLESS_MODE

def cli_mode_example():
    """命令行模式示例"""
    print("\n=== 命令行模式示例 ===")
    
    # 使用上下文管理器确保资源正确清理
    with WebCrawler() as crawler:
        # 设置爬虫
        crawler.setup(
            browser_type=DEFAULT_BROWSER,
            headless=HEADLESS_MODE
        )
        
        # 爬取单个URL
        print("\n1. 爬取单个URL")
        results = crawler.crawl_urls(["https://example.com"])
        if results:
            print(f"标题: {results[0]['title']}")
            print(f"内容长度: {len(results[0]['content'])} 字符")
        
        # 提取文本内容
        print("\n2. 提取文本内容")
        text_content = crawler.extract_text_content("body")
        print(f"文本内容: {text_content[:200]}...")
        
        # 批量爬取多个URL
        print("\n3. 批量爬取")
        urls = [
            "https://example.com",
            "https://example.org"
        ]
        results = crawler.crawl_urls(urls)
        for result in results:
            print(f"\nURL: {result['url']}")
            print(f"标题: {result['title']}")

def api_mode_example():
    """API模式示例"""
    print("\n=== API模式示例 ===")
    
    base_url = "http://localhost:5000"
    
    def call_api(endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用API并返回JSON响应"""
        if data:
            response = requests.post(f"{base_url}{endpoint}", json=data)
        else:
            response = requests.get(f"{base_url}{endpoint}")
        response.raise_for_status()
        return response.json()
    
    try:
        # 检查API状态
        print("\n1. 检查API状态")
        status = call_api("/api/status")
        print(f"API状态: {json.dumps(status, indent=2)}")
        
        # 提取单个URL内容
        print("\n2. 提取URL内容")
        result = call_api("/api/extract", {
            "url": "https://example.com",
            "options": {
                "browser": DEFAULT_BROWSER,
                "headless": True
            }
        })
        print(f"提取结果: {json.dumps(result, indent=2)}")
        
        # 提取文本内容
        print("\n3. 提取文本内容")
        result = call_api("/api/extract-text", {
            "url": "https://example.com",
            "selector": "body",
            "options": {
                "browser": DEFAULT_BROWSER,
                "headless": True
            }
        })
        print(f"文本内容: {result['text_content'][:200]}...")
        
        # 批量提取
        print("\n4. 批量提取")
        result = call_api("/api/batch", {
            "urls": [
                "https://example.com",
                "https://example.org"
            ],
            "options": {
                "browser": DEFAULT_BROWSER,
                "headless": True
            }
        })
        print(f"批量提取结果: {json.dumps(result, indent=2)}")
        
    except requests.exceptions.RequestException as e:
        print(f"API调用失败: {e}")
        print("请确保API服务器正在运行（python src/main.py server）")

def main():
    """主函数"""
    print("Selenium Web Crawler 使用示例")
    print("=" * 50)
    
    try:
        # 运行命令行模式示例
        cli_mode_example()
        
        # 运行API模式示例
        api_mode_example()
        
    except KeyboardInterrupt:
        print("\n程序已终止")
    except Exception as e:
        print(f"\n发生错误: {e}")

if __name__ == "__main__":
    main()