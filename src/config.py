"""
配置参数模块
包含爬虫系统的所有可配置参数
"""

# WebDriver配置
REMOTE_WEBDRIVER_URL = "http://172.16.101.252:4444/wd/hub"
DEFAULT_BROWSER = "chrome"  # 支持 "chrome" 或 "firefox"
HEADLESS_MODE = True  # 无头模式
PAGE_LOAD_TIMEOUT = 30  # 页面加载超时时间（秒）
PAGE_WAIT_TIMEOUT = 15  # 页面元素等待时间（秒）

# 爬取配置
MAX_PAGE_DEPTH = 5  # 最大翻页深度
RETRY_COUNT = 3  # 失败重试次数
WAIT_BETWEEN_PAGES = (0.5, 2)  # 页面间随机等待时间范围（秒）

# 输出配置
OUTPUT_DIR = "./output"  # 数据存储目录
OUTPUT_FORMAT = ["txt", "json"]  # 支持的输出格式

# 资源限制
MAX_TASK_RUNTIME = 3600  # 单任务最大运行时间（秒）
MAX_DAILY_URLS = 1000  # 每日URL处理上限

# 日志配置
LOG_LEVEL = "INFO"  # 日志级别
LOG_FILE = "./logs/crawler.log"  # 日志文件路径
ERROR_LOG = "./logs/error.log"  # 错误日志文件路径