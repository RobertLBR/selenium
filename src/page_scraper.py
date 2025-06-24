"""
页面爬取模块
负责页面内容爬取和分页处理
"""

import time
import random
import re
import html
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
        if not text:
            return ""
            
        # 解码HTML实体
        text = html.unescape(text)
        
        # 移除多余的空白字符
        text = ' '.join(text.split())
        
        # 移除特殊字符和控制字符
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
        
        # 替换URL为标记
        text = re.sub(r'https?://\S+|www\.\S+', '[URL]', text)
        
        # 替换邮箱地址为标记
        text = re.sub(r'\S+@\S+\.\S+', '[EMAIL]', text)
        
        # 移除连续的标点符号
        text = re.sub(r'([.!?])\1+', r'\1', text)
        
        # 移除JavaScript代码片段
        text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
        
        # 移除CSS代码片段
        text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL)
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
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
                "//*[not(self::script or self::style) and not(self::meta) and not(self::link) and string-length(normalize-space(text())) > 0]"
            )
            
            # 提取并清理文本
            texts = [self._clean_text(elem.text) for elem in text_elements if elem.text and elem.text.strip()]
            
            # 获取所有链接
            links = [
                elem.get_attribute('href')
                for elem in self.driver.find_elements(By.TAG_NAME, "a")
                if elem.get_attribute('href')
            ]
            
            # 提取元数据
            metadata = self._extract_metadata()
            
            # 检测内容类型
            content_type = self._detect_content_type(texts)
            
            # 提取结构化数据
            structured_data = self._extract_structured_data()
            
            return {
                "title": title,
                "url": url,
                "body_text": self._clean_text(body_text),
                "text_elements": texts,
                "links": links,
                "metadata": metadata,
                "content_type": content_type,
                "structured_data": structured_data,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"提取页面内容时出错: {str(e)}")
            raise PageLoadError(f"无法提取页面内容: {str(e)}")
            
    def _extract_metadata(self) -> Dict[str, Any]:
        """
        提取页面元数据
        
        Returns:
            Dict[str, Any]: 元数据字典
        """
        metadata = {}
        
        try:
            # 提取meta标签
            meta_tags = {
                "description": "name",
                "keywords": "name",
                "author": "name",
                "viewport": "name",
                "robots": "name",
                "generator": "name",
                "application-name": "name",
                "og:title": "property",
                "og:description": "property",
                "og:image": "property",
                "og:url": "property",
                "og:type": "property",
                "og:site_name": "property",
                "twitter:card": "name",
                "twitter:site": "name",
                "twitter:title": "name",
                "twitter:description": "name",
                "twitter:image": "name"
            }
            
            for tag, attr_type in meta_tags.items():
                try:
                    element = self.driver.find_element(By.XPATH, f"//meta[@{attr_type}='{tag}']")
                    metadata[tag] = element.get_attribute("content")
                except NoSuchElementException:
                    pass
                    
            # 提取canonical链接
            try:
                canonical = self.driver.find_element(By.XPATH, "//link[@rel='canonical']")
                metadata["canonical"] = canonical.get_attribute("href")
            except NoSuchElementException:
                pass
                
            # 提取favicon
            try:
                favicon = self.driver.find_element(By.XPATH, "//link[contains(@rel, 'icon')]")
                metadata["favicon"] = favicon.get_attribute("href")
            except NoSuchElementException:
                pass
                
            # 提取语言
            try:
                html_tag = self.driver.find_element(By.TAG_NAME, "html")
                metadata["language"] = html_tag.get_attribute("lang")
            except NoSuchElementException:
                pass
                
        except Exception as e:
            logger.warning(f"提取元数据时出错: {str(e)}")
            
        return metadata
        
    def _detect_content_type(self, texts: List[str]) -> str:
        """
        检测页面内容类型
        
        Args:
            texts: 页面文本元素列表
            
        Returns:
            str: 内容类型
        """
        # 简单的内容类型检测逻辑
        if not texts:
            return "unknown"
            
        # 检查是否为文章页面
        article_indicators = ["article", "post", "blog", "news"]
        for indicator in article_indicators:
            if indicator in self.driver.current_url.lower():
                return "article"
                
        # 检查是否为产品页面
        product_indicators = ["product", "item", "shop", "store", "buy", "price"]
        for indicator in product_indicators:
            if indicator in self.driver.current_url.lower():
                return "product"
                
        # 检查是否为列表页面
        if len(self.driver.find_elements(By.XPATH, "//ul/li")) > 10:
            return "list"
            
        # 检查是否为表单页面
        if len(self.driver.find_elements(By.TAG_NAME, "form")) > 0:
            return "form"
            
        # 默认为一般页面
        return "general"
        
    def _extract_structured_data(self) -> List[Dict[str, Any]]:
        """
        提取页面中的结构化数据
        
        Returns:
            List[Dict[str, Any]]: 结构化数据列表
        """
        structured_data = []
        
        try:
            # 提取JSON-LD结构化数据
            json_ld_scripts = self.driver.find_elements(
                By.XPATH,
                "//script[@type='application/ld+json']"
            )
            
            for script in json_ld_scripts:
                try:
                    script_content = script.get_attribute("innerHTML")
                    if script_content:
                        # 注意：这里我们只返回原始JSON字符串，实际使用时可以解析为Python对象
                        structured_data.append({
                            "type": "json-ld",
                            "content": script_content
                        })
                except Exception as e:
                    logger.debug(f"提取JSON-LD数据时出错: {str(e)}")
                    
        except Exception as e:
            logger.warning(f"提取结构化数据时出错: {str(e)}")
            
        return structured_data
    
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