"""
WebCrawler 类的单元测试
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.crawler import WebCrawler
from src.config import DEFAULT_BROWSER, HEADLESS_MODE

def test_crawler_initialization():
    """测试爬虫初始化"""
    crawler = WebCrawler()
    assert crawler is not None
    assert crawler.driver is None
    assert crawler.browser_type == DEFAULT_BROWSER
    assert crawler.headless == HEADLESS_MODE

def test_crawler_setup():
    """测试爬虫设置"""
    crawler = WebCrawler()
    crawler.setup(browser_type="chrome", headless=True)
    
    try:
        assert crawler.driver is not None
        assert crawler.browser_type == "chrome"
        assert crawler.headless is True
    finally:
        crawler.cleanup()

def test_crawler_cleanup():
    """测试爬虫清理"""
    crawler = WebCrawler()
    crawler.setup()
    
    assert crawler.driver is not None
    crawler.cleanup()
    assert crawler.driver is None

def test_crawl_single_url():
    """测试单个URL爬取"""
    crawler = WebCrawler()
    crawler.setup()
    
    try:
        # 爬取示例网页
        results = crawler.crawl_urls(["https://example.com"])
        
        assert len(results) == 1
        result = results[0]
        
        assert result["url"] == "https://example.com"
        assert result["title"] == "Example Domain"
        assert "Example Domain" in result["content"]
        
    finally:
        crawler.cleanup()

def test_crawl_multiple_urls():
    """测试多个URL爬取"""
    crawler = WebCrawler()
    crawler.setup()
    
    try:
        # 爬取多个示例网页
        urls = [
            "https://example.com",
            "https://example.org"
        ]
        results = crawler.crawl_urls(urls)
        
        assert len(results) == 2
        
        for result, url in zip(results, urls):
            assert result["url"] == url
            assert "Example Domain" in result["title"]
            assert "Example Domain" in result["content"]
            
    finally:
        crawler.cleanup()

def test_extract_text_content():
    """测试文本内容提取"""
    crawler = WebCrawler()
    crawler.setup()
    
    try:
        # 访问示例网页
        crawler.crawl_urls(["https://example.com"])
        
        # 提取文本内容
        text = crawler.extract_text_content("body")
        
        assert "Example Domain" in text
        assert "This domain is for use in illustrative examples" in text
        
    finally:
        crawler.cleanup()

def test_invalid_url():
    """测试无效URL处理"""
    crawler = WebCrawler()
    crawler.setup()
    
    try:
        results = crawler.crawl_urls(["https://this-is-an-invalid-domain-123456.com"])
        assert len(results) == 0
    finally:
        crawler.cleanup()

def test_context_manager():
    """测试上下文管理器"""
    with WebCrawler() as crawler:
        assert crawler.driver is not None
        results = crawler.crawl_urls(["https://example.com"])
        assert len(results) == 1
        
    # 退出上下文后，driver应该被清理
    assert crawler.driver is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])