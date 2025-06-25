from typing import Dict
from ..plugin_base import PluginBase

class AjaxPlugin:
    """处理AJAX请求的输入层插件"""
    def can_handle(self, url: str) -> bool:
        """检查URL是否包含/ajax/路径"""
        return "/ajax/" in url.lower()
    
    def process_request(self, request: Dict) -> Dict:
        """添加AJAX请求头"""
        if not request.get("headers"):
            request["headers"] = {}
        
        request["headers"].update({
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json"
        })
        return request