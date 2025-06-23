# 网页内容爬取系统

基于Selenium和远程WebDriver的网页内容爬取工具，支持自动处理分页、数据清洗和多种格式输出。提供命令行和API接口两种使用方式。

## 功能特点

- 连接远程WebDriver服务
- 自动爬取页面的完整文本内容
- 智能处理分页内容
- 数据清洗和格式化
- 支持多种输出格式（TXT、JSON）
- 完善的异常处理和日志记录
- 提供RESTful API接口

## 使用方法

系统提供两种使用模式：命令行模式和API服务器模式。

### 命令行模式

#### 基本用法

```bash
python crawler.py cli https://example.com
```

#### 指定浏览器

```bash
python crawler.py cli https://example.com --browser firefox
```

支持的浏览器：`chrome`（默认）、`firefox`

#### 显示浏览器界面（非无头模式）

```bash
python crawler.py cli https://example.com --no-headless
```

#### 不处理分页

```bash
python crawler.py cli https://example.com --no-pagination
```

#### 批量爬取多个URL

```bash
python crawler.py cli https://example.com https://another-example.com
```

### API服务器模式

#### 启动API服务器

```bash
python crawler.py api
```

默认情况下，API服务器会在0.0.0.0:5000上启动。

#### 自定义主机和端口

```bash
python crawler.py api --host 127.0.0.1 --port 8080
```

#### 启用调试模式

```bash
python crawler.py api --debug
```

#### API接口使用

##### 提取网页内容

**请求:**

```
POST /api/extract
Content-Type: application/json

{
  "url": "https://example.com",
  "options": {
    "browser": "chrome",
    "headless": true,
    "handle_pagination": true
  }
}
```

**响应:**

```json
{
  "status": "success",
  "url": "https://example.com",
  "title": "Example Domain",
  "content": "This domain is for use in illustrative examples in documents...",
  "metadata": {
    "author": "Example Author",
    "published_date": "2023-01-01"
  },
  "page_count": 1
}
```

##### 选项说明

- `browser`: 浏览器类型，支持 "chrome"（默认）和 "firefox"
- `headless`: 是否使用无头模式，默认为 true
- `handle_pagination`: 是否处理分页内容，默认为 true

##### 错误响应

当发生错误时，API会返回相应的错误信息：

```json
{
  "status": "error",
  "message": "错误描述信息"
}
```

常见的错误状态码：
- 400: 请求参数错误
- 404: 未找到页面内容
- 500: 服务器内部错误

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

可以通过修改 `src/config.py` 文件来调整系统配置。

## 许可证

MIT