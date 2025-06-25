from typing import Protocol, Dict, Any

class PluginBase(Protocol):
    """插件基础接口协议类"""
    def can_handle(self, url: str) -> bool:
        """判断是否适用当前URL"""
        ...
    
    def process_request(self, request: Dict) -> Dict:
        """处理请求（输入层插件）"""
        ...
    
    def parse(self, response: str) -> Dict[str, Any]:
        """解析响应（解析层插件）"""
        ...
    
    def call_api(self, data: Dict) -> Dict:
        """调用外部接口（接口层插件）"""
        ...