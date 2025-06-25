### **通用爬虫插件开发文档**  
#### **1. 核心架构**  
```plaintext
输入层 → 解析层 → 接口层
```
- **输入层插件**：生成请求（动态渲染、代理轮换等）  
- **解析层插件**：提取数据（XPath/JSON Path/正则）  
- **接口层插件**：调用外部API返回结构化数据  

#### **2. 插件开发规范**  
##### **2.1 插件接口定义**  
```python
from typing import Protocol, Dict, Any

class PluginBase(Protocol):
    def can_handle(self, url: str) -> bool: ...  # 判断是否适用当前URL
    def process_request(self, request: Dict) -> Dict: ...  # 处理请求（输入层）
    def parse(self, response: str) -> Dict[str, Any]: ...  # 解析响应（解析层）
    def call_api(self, data: Dict) -> Dict: ...  # 调用外部接口（接口层）
```

##### **2.2 插件注册机制**  
在 `setup.cfg` 中声明入口点：  
```ini
[options.entry_points]
crawler.plugins =
    ajax_plugin = my_package.ajax:AjaxPlugin
    api_adapter = my_package.api:ApiAdapterPlugin
```

#### **3. 关键插件实现示例**  
##### **3.1 输入层插件（动态渲染）**  
```python
from selenium import webdriver

class AjaxPlugin:
    def can_handle(self, url):
        return "ajax" in url
    
    def process_request(self, request):

        # 配置远程 WebDriver 连接
        remote_url = "http://172.16.101.252:4444/wd/hub"

        # 创建远程 WebDriver 实例
        driver = webdriver.Remote(
            command_executor=remote_url,
            options=options
        )
        driver.get(request["url"])
        return {"html": driver.page_source}  # 返回渲染后的HTML
```

##### **3.2 解析层插件（多格式支持）**  
```python
from parsel import Selector
import json

class NewsParser:
    def parse(self, response):
        selector = Selector(text=response)
        return {
            "title": selector.xpath('//h1/text()').get(),
            "content": selector.css('.article::text').getall()
        }

class JSONParser:
    def parse(self, response):
        return json.loads(response)  # 直接解析JSON响应
```

##### **3.3 接口层插件（API适配器）**  
```python
import requests

class ApiAdapterPlugin:
    def call_api(self, data):
        response = requests.post(
            url="https://api.example.com/process",
            json=data,
            headers={"Authorization": "Bearer <TOKEN>"}
        )
        return response.json()  # 返回API的JSON响应
```

#### **4. 接口调用规范**  
##### **4.1 请求格式**  
```json
{
  "url": "https://target.com/page",
  "plugins": ["ajax_plugin", "news_parser"],
  "api_endpoint": "https://api.example.com/process"
}
```

##### **4.2 响应格式**  
遵循通用API设计规范：  
```json
{
  "code": 200,              # 状态码（200=成功）
  "msg": "Success",
  "data": {                 # 解析后的数据
    "title": "Example",
    "content": ["..."]
  },
  "api_response": { ... }   # 接口层返回的原始数据
}
```

#### **5. 安全与扩展**  
- **请求签名**：接口层插件需支持 `appKey+timestamp+nonce` 签名  
- **动态加载**：通过 `importlib` 按需加载插件  
- **配置驱动**：插件参数（如XPath规则）通过JSON配置文件注入  

#### **6. 调试与测试**  
```python
# 单元测试示例（模拟API响应）
from unittest.mock import patch

@patch("requests.post")
def test_api_adapter(mock_post):
    mock_post.return_value.json.return_value = {"result": "ok"}
    plugin = ApiAdapterPlugin()
    assert plugin.call_api({})["result"] == "ok"
```

---

### **文档说明**  
1. **不包含存储层**：数据通过接口层直接返回，无需持久化设计。  
2. **插件热插拔**：新增解析规则时，只需开发新插件并注册入口点。  
3. **完整工具链**：  
   - 动态渲染：Selenium/Puppeteer  
   - 数据提取：XPath/JSON Path  
   - API调用：Requests + OAuth2认证  

> 参考来源：  
> - Scrapy插件机制  
> - 配置驱动爬虫设计  
> - 内容提取器API  
> - 接口设计规范