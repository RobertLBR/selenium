"""
API服务器的单元测试
"""

import json
import threading
import time
import unittest
import requests
from flask import Flask

from src.api_server import app, start_api_server
from src.config import API_HOST, API_PORT

class TestAPIServer(unittest.TestCase):
    """API服务器测试类"""
    
    @classmethod
    def setUpClass(cls):
        """在所有测试之前启动API服务器"""
        # 使用测试配置
        cls.test_port = 5001
        cls.base_url = f"http://127.0.0.1:{cls.test_port}"
        
        # 在单独的线程中启动API服务器
        cls.server_thread = threading.Thread(
            target=start_api_server,
            kwargs={"host": "127.0.0.1", "port": cls.test_port, "debug": False}
        )
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # 等待服务器启动
        time.sleep(1)
    
    def test_index_endpoint(self):
        """测试根端点"""
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("name", data)
        self.assertIn("version", data)
        self.assertIn("endpoints", data)
    
    def test_status_endpoint(self):
        """测试状态端点"""
        response = requests.get(f"{self.base_url}/api/status")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "running")
        self.assertIn("active_crawlers", data)
        self.assertIn("uptime", data)
    
    def test_extract_endpoint_invalid_request(self):
        """测试提取端点 - 无效请求"""
        # 空请求
        response = requests.post(f"{self.base_url}/api/extract", json={})
        self.assertEqual(response.status_code, 400)
        
        # 缺少URL
        response = requests.post(f"{self.base_url}/api/extract", json={"options": {}})
        self.assertEqual(response.status_code, 400)
    
    def test_extract_endpoint_valid_request(self):
        """测试提取端点 - 有效请求"""
        # 注意：这个测试会实际启动浏览器并爬取网页，可能会比较慢
        response = requests.post(
            f"{self.base_url}/api/extract",
            json={"url": "https://example.com", "options": {"headless": True}}
        )
        
        # 如果测试环境没有浏览器，这个测试可能会失败
        # 在这种情况下，我们可以跳过这个测试
        if response.status_code == 500 and "WebDriver" in response.text:
            self.skipTest("WebDriver不可用")
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["url"], "https://example.com")
        self.assertIn("title", data)
        self.assertIn("content", data)
    
    def test_extract_text_endpoint(self):
        """测试提取文本端点"""
        # 注意：这个测试会实际启动浏览器并爬取网页，可能会比较慢
        response = requests.post(
            f"{self.base_url}/api/extract-text",
            json={"url": "https://example.com", "selector": "body", "options": {"headless": True}}
        )
        
        # 如果测试环境没有浏览器，这个测试可能会失败
        if response.status_code == 500 and "WebDriver" in response.text:
            self.skipTest("WebDriver不可用")
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["url"], "https://example.com")
        self.assertIn("title", data)
        self.assertIn("text_content", data)
        self.assertIn("Example Domain", data["text_content"])
    
    def test_batch_endpoint(self):
        """测试批量提取端点"""
        # 注意：这个测试会实际启动浏览器并爬取网页，可能会比较慢
        response = requests.post(
            f"{self.base_url}/api/batch",
            json={
                "urls": ["https://example.com", "https://example.org"],
                "options": {"headless": True}
            }
        )
        
        # 如果测试环境没有浏览器，这个测试可能会失败
        if response.status_code == 500 and "WebDriver" in response.text:
            self.skipTest("WebDriver不可用")
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["count"], 2)
        self.assertEqual(len(data["results"]), 2)
        
        for result, url in zip(data["results"], ["https://example.com", "https://example.org"]):
            self.assertEqual(result["url"], url)
            self.assertIn("title", result)
            self.assertIn("content", result)

if __name__ == "__main__":
    unittest.main()