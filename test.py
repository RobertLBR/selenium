import unittest
from crawler import WebCrawler
from src.plugins.input.ajax_plugin import AjaxPlugin
from src.plugins.parse.news_parser import NewsParser

class TestWebCrawler(unittest.TestCase):
    def setUp(self):
        self.crawler = WebCrawler()

    def test_ajax_plugin(self):
        """测试AJAX插件"""
        plugin = AjaxPlugin()
        self.assertTrue(plugin.can_handle("https://example.com/ajax/data"))
        self.assertFalse(plugin.can_handle("https://example.com/regular/page"))
        
        request = plugin.process_request({})
        self.assertIn("headers", request)
        self.assertEqual(request["headers"]["X-Requested-With"], "XMLHttpRequest")

    def test_news_parser(self):
        """测试新闻解析插件"""
        plugin = NewsParser()
        self.assertTrue(plugin.can_handle("https://example.com/news/article"))
        self.assertFalse(plugin.can_handle("https://example.com/products/item"))

class TestCrawlerIntegration(unittest.TestCase):
    def test_crawler_initialization(self):
        """测试爬虫初始化"""
        crawler = WebCrawler()
        self.assertGreater(len(crawler.input_plugins), 0)
        self.assertGreater(len(crawler.parse_plugins), 0)

if __name__ == '__main__':
    unittest.main()