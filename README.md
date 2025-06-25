# Selenium Web Crawler

一个基于 Selenium 的网页内容爬取系统，支持命令行模式和 API 服务器模式。该系统提供了灵活的配置选项和强大的内容提取功能，可用于网页数据采集、内容分析等场景。

## 功能特点

- 支持 Chrome 和 Firefox 浏览器
- 支持无头模式和有界面模式
- 提供命令行接口和 RESTful API 接口
- 可提取网页 HTML 内容和文本内容
- 支持批量爬取多个 URL
- 可配置的超时和重试机制
- 支持分页内容处理
- 智能等待页面加载
- 灵活的内容选择器配置
- 完善的错误处理机制
- 详细的日志记录

## 项目结构

```
selenium-web-crawler/
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── main.py            # 主入口文件
│   ├── crawler.py         # 爬虫核心实现
│   ├── api_server.py      # API服务器实现
│   └── config.py          # 配置文件
├── tests/                  # 测试目录
│   ├── __init__.py
│   ├── test_crawler.py    # 爬虫测试
│   └── test_api_server.py # API服务器测试
├── examples/              # 示例目录
│   └── basic_usage.py    # 基本使用示例
├── requirements.txt       # 项目依赖
├── README.md             # 项目文档
├── LICENSE               # MIT许可证
└── .gitignore           # Git忽略配置
```

## 安装

### 前提条件

- Python 3.6+
- Chrome 或 Firefox 浏览器
- 对应的 WebDriver（ChromeDriver 或 GeckoDriver）

### 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/yourusername/selenium-web-crawler.git
cd selenium-web-crawler
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 安装 WebDriver

对于 Chrome：
- 下载与你的 Chrome 版本匹配的 [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
- 将 ChromeDriver 添加到系统 PATH 中

对于 Firefox：
- 下载 [GeckoDriver](https://github.com/mozilla/geckodriver/releases)
- 将 GeckoDriver 添加到系统 PATH 中

## 使用方法

### 命令行模式

爬取单个 URL：

```bash
python src/main.py cli https://example.com
```

指定浏览器类型：

```bash
python src/main.py cli https://example.com --browser firefox
```

使用有界面模式（非无头模式）：

```bash
python src/main.py cli https://example.com --no-headless
```

将结果保存到文件：

```bash
python src/main.py cli https://example.com --output result.txt
```

### API 服务器模式

启动 API 服务器：

```bash
python src/main.py server
```

指定主机和端口：

```bash
python src/main.py server --host 127.0.0.1 --port 8080
```

启用调试模式：

```bash
python src/main.py server --debug
```

## API 文档

### 获取 API 状态

```
GET /api/status
```

响应示例：

```json
{
  "status": "running",
  "active_crawlers": 0,
  "uptime": 123.45
}
```

### 提取 URL 内容

```
POST /api/extract
```

请求体：

```json
{
  "url": "https://example.com",
  "options": {
    "browser": "chrome",
    "headless": true,
    "handle_pagination": true
  }
}
```

响应示例：

```json
{
  "status": "success",
  "url": "https://example.com",
  "title": "Example Domain",
  "content": "<!DOCTYPE html><html>...</html>"
}
```

### 提取 URL 文本内容

```
POST /api/extract-text
```

请求体：

```json
{
  "url": "https://example.com",
  "selector": "body",
  "options": {
    "browser": "chrome",
    "headless": true
  }
}
```

响应示例：

```json
{
  "status": "success",
  "url": "https://example.com",
  "title": "Example Domain",
  "text_content": "Example Domain\nThis domain is for use in illustrative examples in documents..."
}
```

### 批量提取多个 URL 内容

```
POST /api/batch
```

请求体：

```json
{
  "urls": [
    "https://example.com",
    "https://example.org"
  ],
  "options": {
    "browser": "chrome",
    "headless": true,
    "handle_pagination": true
  }
}
```

响应示例：

```json
{
  "status": "success",
  "count": 2,
  "results": [
    {
      "url": "https://example.com",
      "title": "Example Domain",
      "content": "<!DOCTYPE html><html>...</html>"
    },
    {
      "url": "https://example.org",
      "title": "Example Domain",
      "content": "<!DOCTYPE html><html>...</html>"
    }
  ]
}
```

## 环境变量配置

可以通过环境变量配置系统的默认行为：

| 环境变量 | 描述 | 默认值 |
|----------|------|--------|
| SELENIUM_BROWSER | 默认浏览器类型 | chrome |
| SELENIUM_HEADLESS | 是否使用无头模式 | true |
| PAGE_LOAD_TIMEOUT | 页面加载超时时间（秒） | 30 |
| PAGE_WAIT_TIMEOUT | 页面等待超时时间（秒） | 10 |
| ELEMENT_WAIT_TIMEOUT | 元素等待超时时间（秒） | 10 |
| API_HOST | API 服务器主机地址 | 0.0.0.0 |
| API_PORT | API 服务器端口 | 5000 |
| API_DEBUG | 是否启用 API 调试模式 | false |
| MAX_RETRIES | 最大重试次数 | 3 |
| RETRY_DELAY | 重试延迟时间（秒） | 2 |
| USER_AGENT | 自定义用户代理 | Mozilla/5.0... |

## 高级使用

### 处理动态加载内容

```python
from src.crawler import WebCrawler

with WebCrawler() as crawler:
    crawler.setup(wait_for_dynamic_content=True)
    results = crawler.crawl_urls(["https://example.com"])
```

### 自定义内容提取

```python
from src.crawler import WebCrawler

with WebCrawler() as crawler:
    crawler.setup()
    crawler.add_custom_extractor(
        name="product_price",
        selector=".price",
        attribute="data-value"
    )
    results = crawler.crawl_urls(["https://example.com/product"])
```

### 处理登录认证

```python
from src.crawler import WebCrawler

with WebCrawler() as crawler:
    crawler.setup()
    crawler.login(
        url="https://example.com/login",
        username="user",
        password="pass",
        username_selector="#username",
        password_selector="#password",
        submit_selector="button[type='submit']"
    )
    results = crawler.crawl_urls(["https://example.com/protected-page"])
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_crawler.py

# 运行带覆盖率报告的测试
python -m pytest tests/ --cov=src
```

### 代码风格检查

```bash
# 运行 flake8
flake8 src/ tests/

# 运行 black 格式化
black src/ tests/
```

## 故障排除

### 常见问题

1. WebDriver 未找到
   - 确保已下载正确版本的 WebDriver
   - 确保 WebDriver 已添加到系统 PATH 中
   - 检查环境变量 CHROME_DRIVER_PATH 或 FIREFOX_DRIVER_PATH

2. 页面加载超时
   - 增加 PAGE_LOAD_TIMEOUT 值
   - 检查网络连接
   - 确认目标网站可访问

3. 元素未找到
   - 检查选择器是否正确
   - 增加 ELEMENT_WAIT_TIMEOUT 值
   - 确认元素是否在页面中动态加载

### 调试技巧

1. 启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. 使用非无头模式调试：
```bash
python src/main.py cli https://example.com --no-headless
```

3. 保存页面快照：
```python
crawler.save_screenshot("debug.png")
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 更新日志

### [1.0.0] - 2024-01-01
- 初始版本发布
- 支持命令行和 API 模式
- 实现基本的网页内容提取功能

### [0.1.0] - 2023-12-01
- 项目初始化
- 基础功能实现

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 作者

* **Your Name** - *Initial work* - [YourGithub](https://github.com/yourusername)

## 致谢

* Selenium 项目
* Python 社区
* 所有贡献者