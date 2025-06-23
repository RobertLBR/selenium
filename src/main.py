"""
主程序入口
整合所有模块，提供完整的爬虫功能
"""

import sys
import argparse
import time
from typing import List, Optional
from urllib.parse import urlparse

import config
from utils import (
    setup_logging,
    get_logger,
    create_output_dirs,
    format_time_duration,
    CrawlerException
)
from driver_manager import DriverManager
from page_scraper import PageScraper
from data_processor import DataProcessor

logger = get_logger(__name__)

class WebCrawler:
    """网页爬虫主类"""
    
    def __init__(self):
        """初始化爬虫系统"""
        # 设置日志
        setup_logging()
        # 创建输出目录
        create_output_dirs()
        
        self.driver_manager = None
        self.page_scraper = None
        self.data_processor = DataProcessor()
        
        logger.info("爬虫系统初始化完成")
    
    def _validate_url(self, url: str) -> bool:
        """
        验证URL是否有效
        
        Args:
            url: 要验证的URL
            
        Returns:
            bool: URL是否有效
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def setup(self, browser_type: str = config.DEFAULT_BROWSER,
             headless: bool = config.HEADLESS_MODE) -> None:
        """
        设置爬虫系统
        
        Args:
            browser_type: 浏览器类型
            headless: 是否使用无头模式
        """
        try:
            # 创建WebDriver管理器
            self.driver_manager = DriverManager(
                browser_type=browser_type,
                headless=headless
            )
            
            # 创建WebDriver实例
            driver = self.driver_manager.create_driver()
            
            # 创建页面爬取器
            self.page_scraper = PageScraper(driver)
            
            logger.info("爬虫系统设置完成")
            
        except Exception as e:
            logger.error(f"爬虫系统设置失败: {str(e)}")
            self.cleanup()
            raise
    
    def cleanup(self) -> None:
        """清理资源"""
        if self.driver_manager:
            self.driver_manager.close()
        logger.info("爬虫系统资源已清理")
    
    def crawl_url(self, url: str, handle_pagination: bool = True) -> None:
        """
        爬取指定URL的内容
        
        Args:
            url: 目标URL
            handle_pagination: 是否处理分页
        """
        if not self._validate_url(url):
            logger.error(f"无效的URL: {url}")
            return
        
        try:
            start_time = time.time()
            logger.info(f"开始爬取URL: {url}")
            
            if handle_pagination:
                # 处理分页内容
                pages_data = []
                for page_data in self.page_scraper.scrape_with_pagination(url):
                    pages_data.append(page_data)
                
                # 合并分页数据
                if pages_data:
                    merged_data = self.data_processor.merge_paginated_data(pages_data)
                    # 保存数据
                    saved_files = self.data_processor.save_data(merged_data)
                    logger.info(f"分页数据已保存: {saved_files}")
            else:
                # 爬取单页内容
                page_data = self.page_scraper.scrape_page(url)
                # 保存数据
                saved_files = self.data_processor.save_data(page_data)
                logger.info(f"页面数据已保存: {saved_files}")
            
            duration = time.time() - start_time
            logger.info(f"URL爬取完成: {url}, 耗时: {format_time_duration(duration)}")
            
        except Exception as e:
            logger.error(f"爬取URL失败: {url}, 错误: {str(e)}")
            raise
    
    def crawl_urls(self, urls: List[str], handle_pagination: bool = True) -> None:
        """
        批量爬取URL列表
        
        Args:
            urls: URL列表
            handle_pagination: 是否处理分页
        """
        total_urls = len(urls)
        successful = 0
        failed = 0
        
        start_time = time.time()
        logger.info(f"开始批量爬取 {total_urls} 个URL")
        
        for index, url in enumerate(urls, 1):
            try:
                logger.info(f"正在处理 [{index}/{total_urls}] {url}")
                self.crawl_url(url, handle_pagination)
                successful += 1
            except Exception as e:
                logger.error(f"处理URL失败 [{index}/{total_urls}] {url}: {str(e)}")
                failed += 1
        
        duration = time.time() - start_time
        logger.info(
            f"批量爬取完成: 总计 {total_urls} 个URL, "
            f"成功 {successful}, 失败 {failed}, "
            f"总耗时: {format_time_duration(duration)}"
        )

def parse_args() -> argparse.Namespace:
    """
    解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="网页内容爬取工具")
    
    parser.add_argument(
        "urls",
        nargs="+",
        help="要爬取的URL列表"
    )
    
    parser.add_argument(
        "--browser",
        choices=["chrome", "firefox"],
        default=config.DEFAULT_BROWSER,
        help="使用的浏览器类型"
    )
    
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="不使用无头模式（显示浏览器界面）"
    )
    
    parser.add_argument(
        "--no-pagination",
        action="store_true",
        help="不处理分页内容"
    )
    
    return parser.parse_args()

def main() -> None:
    """主程序入口"""
    try:
        # 解析命令行参数
        args = parse_args()
        
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
        
    except CrawlerException as e:
        logger.error(f"爬虫错误: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("用户中断执行")
        sys.exit(2)
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        sys.exit(3)

if __name__ == "__main__":
    main()