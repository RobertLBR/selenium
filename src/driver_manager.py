"""
WebDriver管理模块
负责初始化和配置远程WebDriver
"""

import time
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException, TimeoutException

import config
from utils import get_logger, WebDriverError, retry_on_exception

logger = get_logger(__name__)

class DriverManager:
    """WebDriver管理类，负责创建和管理远程WebDriver实例"""
    
    def __init__(self, remote_url: str = config.REMOTE_WEBDRIVER_URL, 
                 browser_type: str = config.DEFAULT_BROWSER,
                 headless: bool = config.HEADLESS_MODE):
        """
        初始化WebDriver管理器
        
        Args:
            remote_url: 远程WebDriver服务URL
            browser_type: 浏览器类型，支持"chrome"或"firefox"
            headless: 是否使用无头模式
        """
        self.remote_url = remote_url
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.driver: Optional[WebDriver] = None
        
        logger.info(f"初始化DriverManager: {browser_type} {'headless' if headless else 'normal'} mode")
    
    def _get_browser_options(self) -> Any:
        """
        根据浏览器类型获取配置选项
        
        Returns:
            浏览器选项对象
        """
        if self.browser_type == "chrome":
            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
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
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
            # 为Chrome设置页面加载策略
            options.page_load_strategy = 'eager'
            return options
        elif self.browser_type == "firefox":
            options = FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            # 为Firefox设置页面加载策略
            options.set_preference('pageLoadStrategy', 'eager')
            return options
        else:
            raise WebDriverError(f"不支持的浏览器类型: {self.browser_type}")
    
    @retry_on_exception(exceptions=(WebDriverException,), logger=logger)
    def create_driver(self) -> WebDriver:
        """
        创建并配置WebDriver实例
        
        Returns:
            WebDriver: 配置好的WebDriver实例
        
        Raises:
            WebDriverError: 如果创建WebDriver失败
        """
        try:
            logger.info(f"正在连接远程WebDriver服务: {self.remote_url}")
            
            options = self._get_browser_options()
            
            self.driver = webdriver.Remote(
                command_executor=self.remote_url,
                options=options
            )
            
            # 设置超时时间
            self.driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(config.PAGE_WAIT_TIMEOUT)
            
            logger.info(f"WebDriver创建成功: {self.browser_type}")
            return self.driver
            
        except WebDriverException as e:
            logger.error(f"创建WebDriver失败: {str(e)}")
            raise WebDriverError(f"无法创建WebDriver: {str(e)}")
    
    def get_driver(self) -> WebDriver:
        """
        获取当前WebDriver实例，如果不存在则创建
        
        Returns:
            WebDriver: WebDriver实例
        """
        if self.driver is None:
            return self.create_driver()
        return self.driver
    
    def navigate_to(self, url: str) -> bool:
        """
        导航到指定URL
        
        Args:
            url: 目标URL
            
        Returns:
            bool: 是否成功导航
            
        Raises:
            WebDriverError: 如果导航失败
        """
        if self.driver is None:
            self.create_driver()
            
        try:
            logger.info(f"正在导航到: {url}")
            self.driver.get(url)
            return True
        except TimeoutException:
            logger.warning(f"导航到 {url} 超时")
            raise WebDriverError(f"页面加载超时: {url}")
        except WebDriverException as e:
            logger.error(f"导航到 {url} 失败: {str(e)}")
            raise WebDriverError(f"导航失败: {str(e)}")
    
    def close(self) -> None:
        """关闭WebDriver实例"""
        if self.driver:
            try:
                logger.info("正在关闭WebDriver")
                self.driver.quit()
            except WebDriverException as e:
                logger.warning(f"关闭WebDriver时出错: {str(e)}")
            finally:
                self.driver = None
    
    def __enter__(self) -> WebDriver:
        """上下文管理器入口"""
        return self.get_driver()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器退出"""
        self.close()