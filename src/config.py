"""
配置模块
包含所有配置参数和默认值
"""

import os
from typing import Dict, Any

# WebDriver配置
USE_REMOTE_WEBDRIVER = os.getenv('USE_REMOTE_WEBDRIVER', 'true').lower() == 'true'
REMOTE_WEBDRIVER_URL = os.getenv('REMOTE_WEBDRIVER_URL', 'http://172.16.101.252:4444/wd/hub')

# 浏览器配置
DEFAULT_BROWSER = os.getenv('SELENIUM_BROWSER', 'chrome')
HEADLESS_MODE = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'
USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

# 超时配置（秒）
PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
PAGE_WAIT_TIMEOUT = int(os.getenv('PAGE_WAIT_TIMEOUT', '10'))
ELEMENT_WAIT_TIMEOUT = int(os.getenv('ELEMENT_WAIT_TIMEOUT', '10'))

# 重试配置
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '2'))

# API服务器配置
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '5000'))
API_DEBUG = os.getenv('API_DEBUG', 'false').lower() == 'true'

# 浏览器驱动配置
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', '')
FIREFOX_DRIVER_PATH = os.getenv('FIREFOX_DRIVER_PATH', '')

# 浏览器选项
BROWSER_OPTIONS: Dict[str, Dict[str, Any]] = {
    'chrome': {
        'arguments': [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-notifications',
            '--disable-infobars',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--window-size=1920,1080'
        ],
        'experimental_options': {
            'excludeSwitches': ['enable-automation', 'enable-logging'],
            'prefs': {
                'profile.default_content_setting_values.notifications': 2,
                'profile.default_content_settings.popups': 0,
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': True
            }
        }
    },
    'firefox': {
        'arguments': [
            '--disable-extensions',
            '--disable-notifications',
            '--disable-infobars',
            '--width=1920',
            '--height=1080'
        ],
        'preferences': {
            'dom.webnotifications.enabled': False,
            'dom.push.enabled': False,
            'browser.download.folderList': 2,
            'browser.download.manager.showWhenStarting': False,
            'browser.helperApps.neverAsk.saveToDisk': 'application/octet-stream'
        }
    }
}

# 页面加载配置
PAGE_LOAD_STRATEGY = 'normal'  # 可选：'normal', 'eager', 'none'
SCROLL_PAUSE_TIME = 1.0  # 滚动页面时的暂停时间（秒）
SCROLL_ATTEMPTS = 5  # 滚动尝试次数

# 分页配置
PAGINATION_SELECTORS = [
    '.pagination a',  # Bootstrap风格
    '.pager a',      # 通用分页
    'a[rel="next"]', # 下一页链接
    '.next a',       # 下一页按钮
    '.load-more'     # 加载更多按钮
]

# 内容提取配置
CONTENT_SELECTORS = {
    'title': ['h1', '.title', '#title'],
    'content': ['article', '.content', '#content', 'main'],
    'text': ['p', '.text', '#text']
}

# 错误消息模板
ERROR_MESSAGES = {
    'browser_not_found': '未找到浏览器驱动程序，请确保已安装 {browser} 浏览器并配置了正确的驱动路径',
    'page_load_timeout': '页面加载超时：{url}',
    'element_not_found': '未找到元素：{selector}',
    'invalid_url': '无效的URL：{url}',
    'connection_error': '连接错误：{url}',
    'extraction_error': '内容提取错误：{error}'
}

def get_browser_options(browser_type: str) -> Dict[str, Any]:
    """
    获取指定浏览器类型的配置选项
    
    Args:
        browser_type: 浏览器类型（chrome或firefox）
        
    Returns:
        Dict[str, Any]: 浏览器配置选项
    """
    return BROWSER_OPTIONS.get(browser_type.lower(), {})

def get_error_message(key: str, **kwargs) -> str:
    """
    获取格式化的错误消息
    
    Args:
        key: 错误消息键
        **kwargs: 格式化参数
        
    Returns:
        str: 格式化后的错误消息
    """
    template = ERROR_MESSAGES.get(key, '未知错误')
    return template.format(**kwargs)