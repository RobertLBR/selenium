#!/usr/bin/env python3
"""
Selenium Web Crawler 主入口模块
提供命令行接口和API服务器启动功能
"""

import sys
import logging
import click
from typing import List, Optional, Dict, Any

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

# 导入爬虫和API服务器
from crawler import WebCrawler
from api_server import start_api_server

@click.group()
def cli():
    """Selenium Web Crawler - 一个基于Selenium的网页内容爬取工具"""
    pass

@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--browser', '-b', default=DEFAULT_BROWSER, 
              type=click.Choice(['chrome', 'firefox']), 
              help='浏览器类型 (默认: chrome)')
@click.option('--headless/--no-headless', default=HEADLESS_MODE, 
              help='是否使用无头模式 (默认: 是)')
@click.option('--output', '-o', type=click.Path(), 
              help='输出文件路径 (默认: 标准输出)')
@click.option('--format', '-f', type=click.Choice(['html', 'text', 'json']), 
              default='html', help='输出格式 (默认: html)')
@click.option('--selector', '-s', default='body', 
              help='用于提取文本内容的CSS选择器 (默认: body)')
@click.option('--handle-pagination/--no-handle-pagination', default=True, 
              help='是否处理分页内容 (默认: 是)')
def crawl(urls: List[str], browser: str, headless: bool, output: Optional[str], 
          format: str, selector: str, handle_pagination: bool):
    """
    爬取指定URL的内容
    
    URLS: 要爬取的一个或多个URL
    """
    logger.info(f"启动爬虫 - 浏览器: {browser}, 无头模式: {headless}")
    logger.info(f"要爬取的URL: {urls}")
    
    results = []
    
    try:
        with WebCrawler() as crawler:
            crawler.setup(browser_type=browser, headless=headless)
            
            if format == 'text':
                # 爬取并提取文本内容
                for url in urls:
                    crawler_results = crawler.crawl_urls([url], handle_pagination=handle_pagination)
                    if crawler_results and len(crawler_results) > 0:
                        text_content = crawler.extract_text_content(selector)
                        results.append({
                            "url": url,
                            "title": crawler_results[0].get("title", ""),
                            "text_content": text_content
                        })
            else:
                # 爬取HTML内容
                results = crawler.crawl_urls(urls, handle_pagination=handle_pagination)
        
        # 处理结果
        if results:
            if output:
                # 写入文件
                with open(output, 'w', encoding='utf-8') as f:
                    if format == 'json':
                        import json
                        json.dump(results, f, ensure_ascii=False, indent=2)
                    elif format == 'text':
                        for result in results:
                            f.write(f"URL: {result['url']}\n")
                            f.write(f"标题: {result['title']}\n")
                            f.write(f"内容:\n{result['text_content']}\n\n")
                    else:  # html
                        for result in results:
                            f.write(f"<!-- URL: {result['url']} -->\n")
                            f.write(f"<!-- 标题: {result['title']} -->\n")
                            f.write(f"{result['content']}\n\n")
                logger.info(f"结果已保存到 {output}")
            else:
                # 输出到标准输出
                if format == 'json':
                    import json
                    print(json.dumps(results, ensure_ascii=False, indent=2))
                elif format == 'text':
                    for result in results:
                        print(f"URL: {result['url']}")
                        print(f"标题: {result['title']}")
                        print(f"内容:\n{result['text_content']}\n")
                else:  # html
                    for result in results:
                        print(f"<!-- URL: {result['url']} -->")
                        print(f"<!-- 标题: {result['title']} -->")
                        print(f"{result['content']}\n")
        else:
            logger.error("未能提取到任何内容")
            sys.exit(1)
            
    except Exception as e:
        logger.exception(f"爬取过程中发生错误: {str(e)}")
        sys.exit(1)

@cli.command()
@click.option('--host', default=API_HOST, help=f'API服务器主机地址 (默认: {API_HOST})')
@click.option('--port', default=API_PORT, type=int, help=f'API服务器端口 (默认: {API_PORT})')
@click.option('--debug/--no-debug', default=API_DEBUG, help=f'是否启用调试模式 (默认: {"是" if API_DEBUG else "否"})')
def server(host: str, port: int, debug: bool):
    """启动API服务器"""
    try:
        start_api_server(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("API服务器已停止")
    except Exception as e:
        logger.exception(f"API服务器启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    cli()