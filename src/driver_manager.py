"""
WebDriver管理模块
负责初始化和配置WebDriver
"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService

# 导入配置
from config import (
    DEFAULT_BROWSER, 
    HEADLESS_MODE, 
    PAGE_LOAD_TIMEOUT, 
    PAGE_WAIT_TIMEOUT,
    USER_AGENT,
    REMOTE_WEBDRIVER_URL,
    USE_REMOTE_WEBDRIVER,
    get_browser_options
)

# 设置日志
logger = logging.getLogger(__name__)

def get_driver(browser_type=DEFAULT_BROWSER, headless=HEADLESS_MODE):
    """
    获取配置好的WebDriver实例
    
    Args:
        browser_type: 浏览器类型，支持"chrome"或"firefox"
        headless: 是否使用无头模式
        
    Returns:
        WebDriver实例
        
    Raises:
        ValueError: 如果指定了不支持的浏览器类型
    """
    logger.info(f"初始化WebDriver: {browser_type} {'headless' if headless else 'normal'} mode")
    
    # 获取浏览器选项配置
    browser_options = get_browser_options(browser_type, headless)
    
    if browser_type.lower() == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless")
        
        # 添加Chrome选项
        options.add_argument(f"--user-agent={USER_AGENT}")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-translate")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        
        # 设置页面加载策略
        options.page_load_strategy = browser_options.get("page_load_strategy", "eager")
        
        if USE_REMOTE_WEBDRIVER:
            # 使用远程WebDriver
            logger.info(f"使用远程WebDriver: {REMOTE_WEBDRIVER_URL}")
            driver = webdriver.Remote(
                command_executor=REMOTE_WEBDRIVER_URL,
                options=options
            )
        else:
            # 使用本地WebDriver
            service = ChromeService()
            driver = webdriver.Chrome(service=service, options=options)
        
    elif browser_type.lower() == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
            
        # 添加Firefox特定选项
        options.add_argument(f"--width={browser_options.get('width', 1920)}")
        options.add_argument(f"--height={browser_options.get('height', 1080)}")
        
        # 设置用户代理
        options.set_preference("general.useragent.override", USER_AGENT)
        
        # 设置页面加载策略
        options.set_preference("pageLoadStrategy", browser_options.get("page_load_strategy", "eager"))
        
        if USE_REMOTE_WEBDRIVER:
            # 使用远程WebDriver
            logger.info(f"使用远程WebDriver: {REMOTE_WEBDRIVER_URL}")
            driver = webdriver.Remote(
                command_executor=REMOTE_WEBDRIVER_URL,
                options=options
            )
        else:
            # 使用本地WebDriver
            service = FirefoxService()
            driver = webdriver.Firefox(service=service, options=options)
        
    else:
        logger.error(f"不支持的浏览器类型: {browser_type}")
        raise ValueError(f"不支持的浏览器类型: {browser_type}")
    
    # 设置超时时间
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    driver.implicitly_wait(PAGE_WAIT_TIMEOUT)
    
    logger.info(f"WebDriver初始化成功: {browser_type}")
    return driver