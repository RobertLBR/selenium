"""
页面爬取模块
负责页面内容爬取和分页处理
"""

import time
import random
from typing import List, Dict, Optional, Generator, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)

import config
from utils import get_logger, PageLoadError, retry_on_exception

logger = get_logger(__name__)

class PageScraper:
    """页面爬取类，负责获取页面内容和处理分页"""
    
    def __init__(self, driver: WebDriver):
        """
        初始化页面爬取器
        
        Args:
            driver: WebDriver实例
        """
        self.driver = driver
        self.wait = WebDriverWait(
            driver,
            config.PAGE_WAIT_TIMEOUT,
            poll_frequency=0.5,
            ignored_exceptions=(StaleElementReferenceException,)
        )
    
    def _random_wait(self) -> None:
        """在操作之间随机等待，避免被反爬"""
        min_wait, max_wait = config.WAIT_BETWEEN_PAGES
        time.sleep(random.uniform(min_wait, max_wait))
    
    def _scroll_page(self) -> None:
        """
        滚动页面到底部，确保加载所有动态内容
        """
        try:
            # 获取初始页面高度
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # 滚动到底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # 等待页面加载
                time.sleep(1)
                
                # 计算新的页面高度
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                # 如果页面高度没有变化，说明已经到底部
                if new_height == last_height:
                    break
                    
                last_height = new_height
                
        except Exception as e:
            logger.warning(f"页面滚动时出错: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理后的文本
        """
        # 移除多余的空白字符
        text = ' '.join(text.split())
        return text.strip()
    
    def _extract_page_content(self) -> Dict[str, Any]:
        """
        提取当前页面的内容
        
        Returns:
            Dict[str, Any]: 包含页面内容的字典
        """
        try:
            # 等待页面主体加载完成
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 滚动页面以加载动态内容
            self._scroll_page()
            
            # 获取页面标题
            title = self.driver.title
            
            # 获取页面URL
            url = self.driver.current_url
            
            # 获取页面主要文本内容
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # 获取所有可见文本元素
            text_elements = self.driver.find_elements(
                By.XPATH,
                "//*[not(self::script or self::style)]/text()[normalize-space()]"
            )
            
            # 提取并清理文本
            texts = [self._clean_text(elem.text) for elem in text_elements if elem.text.strip()]
            
            # 获取所有链接
            links = [
                elem.get_attribute('href')
                for elem in self.driver.find_elements(By.TAG_NAME, "a")
                if elem.get_attribute('href')
            ]
            
            return {
                "title": title,
                "url": url,
                "body_text": self._clean_text(body_text),
                "text_elements": texts,
                "links": links,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"提取页面内容时出错: {str(e)}")
            raise PageLoadError(f"无法提取页面内容: {str(e)}")
    
    def _find_next_page_link(self) -> Optional[str]:
        """
        查找下一页链接
        
        Returns:
            Optional[str]: 下一页URL，如果没有下一页则返回None
        """
        # 常见的下一页按钮模式
        next_page_patterns = [
            "//a[contains(text(), '下一页')]",
            "//a[contains(text(), 'Next')]",
            "//a[contains(@class, 'next')]",
            "//a[contains(@rel, 'next')]",
            "//a[contains(@aria-label, 'Next')]",
            "//button[contains(text(), '下一页')]",
            "//button[contains(text(), 'Next')]"
        ]
        
        for pattern in next_page_patterns:
            try:
                element = self.driver.find_element(By.XPATH, pattern)
                if element.is_displayed() and element.is_enabled():
                    return element.get_attribute('href')
            except NoSuchElementException:
                continue
            
        return None
    
    @retry_on_exception(exceptions=(PageLoadError, TimeoutException), logger=logger)
    def scrape_page(self, url: str) -> Dict[str, Any]:
        """
        爬取单个页面的内容
        
        Args:
            url: 目标页面URL
            
        Returns:
            Dict[str, Any]: 页面内容
            
        Raises:
            PageLoadError: 如果页面爬取失败
        """
        try:
            logger.info(f"开始爬取页面: {url}")
            
            # 导航到页面
            self.driver.get(url)
            
            # 随机等待
            self._random_wait()
            
            # 提取页面内容
            content = self._extract_page_content()
            
            logger.info(f"页面爬取成功: {url}")
            return content
            
        except Exception as e:
            logger.error(f"爬取页面失败: {url}, 错误: {str(e)}")
            raise PageLoadError(f"爬取页面失败: {str(e)}")
    
    def scrape_with_pagination(self, start_url: str) -> Generator[Dict[str, Any], None, None]:
        """
        爬取包含分页的页面内容
        
        Args:
            start_url: 起始页面URL
            
        Yields:
            Dict[str, Any]: 每个页面的内容
        """
        current_url = start_url
        page_count = 0
        
        while current_url and page_count < config.MAX_PAGE_DEPTH:
            try:
                # 爬取当前页面
                content = self.scrape_page(current_url)
                yield content
                
                page_count += 1
                logger.info(f"已完成第 {page_count} 页的爬取")
                
                # 查找下一页链接
                next_url = self._find_next_page_link()
                
                if not next_url:
                    logger.info("没有找到下一页链接，爬取结束")
                    break
                    
                current_url = next_url
                self._random_wait()
                
            except PageLoadError as e:
                logger.error(f"处理分页时出错: {str(e)}")
                break
            except Exception as e:
                logger.error(f"未预期的错误: {str(e)}")
                break
        
        logger.info(f"分页爬取完成，共爬取 {page_count} 页")