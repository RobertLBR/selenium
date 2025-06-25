from typing import Dict
import requests
from ..plugin_base import PluginBase

class ApiAdapterPlugin:
    """外部API适配插件"""
    def can_handle(self, url: str) -> bool:
        """检查URL是否指向我们的API端点"""
        return url.startswith("https://api.example.com/")
    
    def call_api(self, data: Dict) -> Dict:
        """调用外部API并返回结果"""
        endpoint = data.get("endpoint", "/v1/data")
        params = data.get("params", {})
        
        response = requests.get(
            f"https://api.example.com{endpoint}",
            params=params,
            headers={"Authorization": "Bearer YOUR_API_KEY"}
        )
        
        return {
            "status": response.status_code,
            "data": response.json()
        }