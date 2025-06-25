#!/usr/bin/env python
"""
网页内容爬取系统入口脚本
支持命令行模式和API服务器模式
"""

import sys
import argparse
from main import WebCrawler
from api_server import start_api_server

def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="网页内容爬取系统")
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest="mode", help="运行模式")
    
    # CLI模式解析器
    cli_parser = subparsers.add_parser("cli", help="命令行模式")
    cli_parser.add_argument(
        "urls",
        nargs="+",
        help="要爬取的URL列表"
    )
    cli_parser.add_argument(
        "--browser",
        choices=["chrome", "firefox"],
        help="使用的浏览器类型"
    )
    cli_parser.add_argument(
        "--no-headless",
        action="store_true",
        help="不使用无头模式（显示浏览器界面）"
    )
    cli_parser.add_argument(
        "--no-pagination",
        action="store_true",
        help="不处理分页内容"
    )
    
    # API服务器模式解析器
    api_parser = subparsers.add_parser("api", help="API服务器模式")
    api_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API服务器监听地址"
    )
    api_parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="API服务器监听端口"
    )
    api_parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )
    
    return parser.parse_args()

def run_cli_mode(args):
    """运行命令行模式"""
    try:
        # 创建爬虫实例
        crawler = WebCrawler()
        
        # 设置爬虫
        crawler.setup(
            browser_type=args.browser,
            headless=not args.no_headless
        )
        
        try:
            # 执行爬取
            crawler.crawl_urls(
                args.urls,
                handle_pagination=not args.no_pagination
            )
        finally:
            # 清理资源
            crawler.cleanup()
        
        sys.exit(0)
        
    except Exception as e:
        print(f"爬虫错误: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("用户中断执行")
        sys.exit(2)

if __name__ == "__main__":
    args = parse_args()
    
    if args.mode == "api":
        # API服务器模式
        start_api_server(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    elif args.mode == "cli":
        # 命令行模式
        run_cli_mode(args)
    else:
        print("请指定运行模式: cli 或 api")
        sys.exit(1)
