# 网络爬虫插件系统

一个基于三层架构的灵活爬虫插件系统。

## 项目功能

- **模块化设计**：输入层、解析层和接口层分离
- **易于扩展**：可轻松添加针对不同网站的新插件
- **类型提示**：完整的Python类型提示支持
- **标准化接口**：所有插件遵循相同的接口规范

## 目录结构

```
web-crawler-plugins/
├── README.md          # 项目说明文档
├── setup.cfg          # 插件注册配置文件
├── src/               # 源代码目录
│   ├── plugin_base.py # 插件基础接口
│   └── plugins/       # 插件实现
│       ├── input/     # 输入层插件
│       │   └── ajax_plugin.py
│       ├── parse/     # 解析层插件
│       │   └── news_parser.py
│       └── api/       # 接口层插件
│           └── api_adapter.py
└── test.py            # 测试文件
```

## 运行方式

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/your-repo/web-crawler-plugins.git
cd web-crawler-plugins
```

2. 安装依赖
```bash
pip install -e .
```

### 使用示例

```python
from src.plugin_base import PluginBase
from src.plugins.input.ajax_plugin import AjaxPlugin
from src.plugins.parse.news_parser import NewsParser

# 初始化插件
input_plugin = AjaxPlugin()
parse_plugin = NewsParser()

# 处理请求
if input_plugin.can_handle(url):
    request = input_plugin.process_request({})
    
# 解析内容
if parse_plugin.can_handle(url):
    result = parse_plugin.parse(html_content)
```

### 内置插件列表

| 插件类型 | 类名            | 功能描述               |
|----------|-----------------|-----------------------|
| 输入层   | AjaxPlugin      | 处理AJAX请求          |
| 解析层   | NewsParser      | 解析新闻文章内容       |
| 接口层   | ApiAdapterPlugin| 适配外部API调用       |

## 开发新插件

1. 实现插件基类
```python
from src.plugin_base import PluginBase

class MyPlugin:
    def can_handle(self, url: str) -> bool:
        """判断是否适用当前URL"""
        pass
    
    def process_request(self, request: Dict) -> Dict:
        """处理请求(输入层插件)"""
        pass
```

2. 注册插件
在setup.cfg中添加：
```ini
[options.entry_points]
web_crawler.input_plugins =
    my_plugin = src.plugins.input.my_plugin:MyPlugin
```

## 贡献指南

1. Fork本仓库
2. 创建您的特性分支
3. 提交您的修改
4. 推送分支
5. 创建Pull Request

## 许可证

MIT