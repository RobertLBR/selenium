from typing import Dict, Any
from bs4 import BeautifulSoup
from ..plugin_base import PluginBase

class NewsParser:
    """新闻内容解析插件"""
    def can_handle(self, url: str) -> bool:
        """检查URL是否包含/news/路径"""
        return "/news/" in url.lower()
    
    def parse(self, response: str) -> Dict[str, Any]:
        """解析新闻页面内容"""
        soup = BeautifulSoup(response, "html.parser")
        
        title = soup.find("h1").text.strip() if soup.find("h1") else ""
        content = "\n".join(p.text.strip() for p in soup.find_all("p"))
        date = soup.find("time")["datetime"] if soup.find("time") else ""
        
        return {
            "title": title,
            "content": content,
            "date": date,
            "type": "news"
        }