"""
数据处理模块
负责数据清洗、格式化和输出
"""

import os
import json
import re
from typing import Dict, List, Any, Union, Optional
from datetime import datetime

import config
from utils import get_logger, DataProcessError, sanitize_filename, get_timestamp

logger = get_logger(__name__)

class DataProcessor:
    """数据处理类，负责清洗和保存爬取的数据"""
    
    def __init__(self, output_dir: str = config.OUTPUT_DIR):
        """
        初始化数据处理器
        
        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"数据处理器初始化，输出目录: {output_dir}")
    
    def clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗爬取的数据
        
        Args:
            data: 原始爬取数据
            
        Returns:
            Dict[str, Any]: 清洗后的数据
        """
        cleaned_data = data.copy()
        
        # 清理标题
        if "title" in cleaned_data:
            cleaned_data["title"] = self._clean_text(cleaned_data["title"])
        
        # 清理正文
        if "body_text" in cleaned_data:
            cleaned_data["body_text"] = self._clean_text(cleaned_data["body_text"])
        
        # 清理文本元素列表
        if "text_elements" in cleaned_data:
            cleaned_data["text_elements"] = [
                self._clean_text(text) for text in cleaned_data["text_elements"]
                if text and self._clean_text(text)
            ]
        
        # 清理链接
        if "links" in cleaned_data:
            cleaned_data["links"] = [
                link for link in cleaned_data["links"]
                if link and link.startswith(("http://", "https://"))
            ]
        
        # 添加处理时间戳
        cleaned_data["processed_at"] = datetime.now().isoformat()
        
        return cleaned_data
    
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
            
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # 移除多余空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s.,;:!?\'\"()-]', ' ', text)
        
        # 移除空行
        text = re.sub(r'^\s*$', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def extract_main_content(self, data: Dict[str, Any]) -> str:
        """
        从爬取数据中提取主要内容
        
        Args:
            data: 爬取的数据
            
        Returns:
            str: 提取的主要内容
        """
        # 如果有清理过的正文，直接使用
        if "body_text" in data and data["body_text"]:
            return data["body_text"]
        
        # 否则，合并所有文本元素
        if "text_elements" in data and data["text_elements"]:
            return "\n\n".join(data["text_elements"])
        
        return ""
    
    def save_as_text(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        将数据保存为文本文件
        
        Args:
            data: 要保存的数据
            filename: 文件名（可选）
            
        Returns:
            str: 保存的文件路径
        """
        try:
            # 生成文件名
            if not filename:
                title = sanitize_filename(data.get("title", "untitled"))
                timestamp = get_timestamp()
                filename = f"{title}_{timestamp}.txt"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # 提取主要内容
            content = self.extract_main_content(data)
            
            # 添加元数据
            metadata = (
                f"标题: {data.get('title', '无标题')}\n"
                f"URL: {data.get('url', '未知')}\n"
                f"爬取时间: {datetime.fromtimestamp(data.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"处理时间: {data.get('processed_at', datetime.now().isoformat())}\n"
                f"{'-' * 80}\n\n"
            )
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(metadata)
                f.write(content)
            
            logger.info(f"数据已保存为文本文件: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"保存文本文件失败: {str(e)}")
            raise DataProcessError(f"保存文本文件失败: {str(e)}")
    
    def save_as_json(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        将数据保存为JSON文件
        
        Args:
            data: 要保存的数据
            filename: 文件名（可选）
            
        Returns:
            str: 保存的文件路径
        """
        try:
            # 生成文件名
            if not filename:
                title = sanitize_filename(data.get("title", "untitled"))
                timestamp = get_timestamp()
                filename = f"{title}_{timestamp}.json"
            
            filepath = os.path.join(self.output_dir, filename)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已保存为JSON文件: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"保存JSON文件失败: {str(e)}")
            raise DataProcessError(f"保存JSON文件失败: {str(e)}")
    
    def save_data(self, data: Dict[str, Any], formats: List[str] = config.OUTPUT_FORMAT) -> Dict[str, str]:
        """
        将数据保存为指定格式
        
        Args:
            data: 要保存的数据
            formats: 输出格式列表
            
        Returns:
            Dict[str, str]: 格式到文件路径的映射
        """
        # 清洗数据
        cleaned_data = self.clean_data(data)
        
        # 生成基本文件名
        title = sanitize_filename(cleaned_data.get("title", "untitled"))
        timestamp = get_timestamp()
        base_filename = f"{title}_{timestamp}"
        
        result = {}
        
        # 保存为各种格式
        for fmt in formats:
            if fmt.lower() == "txt":
                filepath = self.save_as_text(cleaned_data, f"{base_filename}.txt")
                result["txt"] = filepath
            elif fmt.lower() == "json":
                filepath = self.save_as_json(cleaned_data, f"{base_filename}.json")
                result["json"] = filepath
            else:
                logger.warning(f"不支持的输出格式: {fmt}")
        
        return result
    
    def merge_paginated_data(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        合并分页数据
        
        Args:
            pages_data: 多个页面的数据列表
            
        Returns:
            Dict[str, Any]: 合并后的数据
        """
        if not pages_data:
            return {}
        
        # 使用第一页作为基础
        merged_data = pages_data[0].copy()
        
        # 合并文本内容
        all_text = []
        for page in pages_data:
            content = self.extract_main_content(page)
            if content:
                all_text.append(content)
        
        merged_data["body_text"] = "\n\n".join(all_text)
        
        # 合并文本元素
        all_elements = []
        for page in pages_data:
            elements = page.get("text_elements", [])
            all_elements.extend(elements)
        
        merged_data["text_elements"] = all_elements
        
        # 合并链接
        all_links = []
        for page in pages_data:
            links = page.get("links", [])
            all_links.extend(links)
        
        # 去重链接
        merged_data["links"] = list(set(all_links))
        
        # 添加分页信息
        merged_data["page_count"] = len(pages_data)
        merged_data["is_paginated"] = len(pages_data) > 1
        
        return merged_data