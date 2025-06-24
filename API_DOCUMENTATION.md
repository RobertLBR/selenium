# Selenium Web Scraper API 文档

## 概述

Selenium Web Scraper API 是一个基于Flask的RESTful API服务，它使用Selenium WebDriver来爬取网页内容。该API能够处理JavaScript渲染的页面、动态加载的内容以及分页内容，提供结构化的数据输出。

## 基础信息

- **基础URL**: http://localhost:5000
- **支持的请求方法**: POST
- **响应格式**: JSON
- **编码方式**: UTF-8
- **跨域支持**: 是

## API端点

### 1. 提取网页内容

**端点**: `/api/extract`

**方法**: POST

**描述**: 爬取指定URL的网页内容，提取文本、标题和元数据。

#### 请求参数

请求体应为JSON格式，包含以下字段：

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| url | string | 是 | 要爬取的网页URL |
| options | object | 否 | 爬取选项 |
| options.browser | string | 否 | 浏览器类型，可选值："chrome"或"firefox"，默认为"chrome" |
| options.headless | boolean | 否 | 是否使用无头模式，默认为true |
| options.handle_pagination | boolean | 否 | 是否处理分页内容，默认为true |

**请求体示例**:

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

#### 响应

##### 成功响应

状态码: 200 OK

响应体:

| 字段名 | 类型 | 描述 |
|--------|------|------|
| status | string | 状态标识，值为"success" |
| url | string | 请求的URL |
| title | string | 提取的页面标题 |
| content | string | 提取的文本内容 |
| metadata | object | 提取的元数据 |
| metadata.author | string | 作者名称（如果可用） |
| metadata.date | string | 发布日期（如果可用） |
| metadata.category | string | 内容分类（如果可用） |
| page_count | number | 处理的页面数量 |

**响应示例**:

```json
{
    "status": "success",
    "url": "https://example.com",
    "title": "Example Domain",
    "content": "This domain is for use in illustrative examples in documents...",
    "metadata": {
        "author": "IANA",
        "date": "2023-01-01",
        "category": "Example"
    },
    "page_count": 1
}
```

##### 错误响应

状态码: 400 Bad Request, 404 Not Found, 或 500 Internal Server Error

响应体:

| 字段名 | 类型 | 描述 |
|--------|------|------|
| status | string | 状态标识，值为"error" |
| message | string | 错误描述 |

**错误响应示例**:

```json
{
    "status": "error",
    "message": "无效的URL格式"
}
```

## 调用示例

### cURL

```bash
curl -X POST http://localhost:5000/api/extract \
     -H "Content-Type: application/json" \
     -d '{
         "url": "https://example.com",
         "options": {
             "browser": "chrome",
             "headless": true,
             "handle_pagination": true
         }
     }'
```

### Python

```python
import requests

response = requests.post(
    'http://localhost:5000/api/extract',
    json={
        'url': 'https://example.com',
        'options': {
            'browser': 'chrome',
            'headless': True,
            'handle_pagination': True
        }
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"页面标题: {data['title']}")
    print(f"内容长度: {len(data['content'])} 字符")
else:
    print(f"错误: {response.json()['message']}")
```

### JavaScript

```javascript
fetch('http://localhost:5000/api/extract', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        url: 'https://example.com',
        options: {
            browser: 'chrome',
            headless: true,
            handle_pagination: true
        }
    })
})
.then(response => response.json())
.then(data => {
    if (data.status === 'success') {
        console.log(`页面标题: ${data.title}`);
        console.log(`内容长度: ${data.content.length} 字符`);
    } else {
        console.error(`错误: ${data.message}`);
    }
})
.catch(error => console.error('请求失败:', error));
```

## 错误处理

### 常见错误代码

| 状态码 | 错误类型 | 可能原因 |
|--------|----------|----------|
| 400 | 请求参数错误 | 无效的URL格式、缺少必需参数、无效的JSON格式 |
| 404 | 未找到内容 | 页面不存在、内容无法提取 |
| 500 | 服务器内部错误 | 浏览器启动失败、内存不足、网络问题 |

### 错误处理最佳实践

1. 始终检查响应的`status`字段，确认是"success"还是"error"
2. 对于状态码为5xx的错误，考虑实现重试机制
3. 对于状态码为4xx的错误，检查请求参数是否正确
4. 记录详细的错误信息，包括请求参数和响应内容，以便调试

## 性能考虑

1. **请求超时**: 对于大型网页或多页内容，请求可能需要较长时间。考虑在客户端设置适当的超时时间。
2. **并发请求**: API服务器有并发限制，避免发送过多并发请求。
3. **资源使用**: 每个请求都会启动一个浏览器实例，消耗较多系统资源。在高负载情况下，考虑使用队列系统。

## 限制和注意事项

1. **反爬虫机制**: 某些网站可能有反爬虫机制，可能导致内容提取失败或不完整。
2. **动态内容**: 对于高度动态的内容，可能需要调整爬取策略。
3. **内容变化**: 网站结构变化可能导致提取结果不一致。
4. **法律合规**: 确保爬取行为符合目标网站的服务条款和相关法律法规。

## 安全建议

1. 在生产环境中启用HTTPS
2. 实现适当的API认证机制
3. 限制API的访问频率
4. 定期更新依赖库，特别是Selenium和浏览器驱动

## 常见问题解答

### Q: API返回"浏览器启动失败"错误怎么办？

A: 确保系统已安装相应的浏览器和WebDriver，并且版本兼容。检查系统资源是否充足。

### Q: 如何处理需要登录的网站？

A: 当前版本不直接支持会话管理。考虑先手动登录并获取cookies，然后在请求中提供这些cookies。

### Q: 如何提高爬取速度？

A: 考虑使用headless模式，减少等待时间，或者使用并行处理多个请求。

### Q: 如何处理CAPTCHA或其他反爬虫机制？

A: 当前版本没有内置的CAPTCHA处理。对于简单的反爬虫机制，可以尝试调整请求头和爬取间隔。

## 版本历史

- **v1.0.0** - 初始版本，支持基本的网页内容提取
- **v1.1.0** - 添加分页处理功能
- **v1.2.0** - 添加元数据提取功能