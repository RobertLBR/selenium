"""
工具函数模块
提供日志记录、异常处理等通用功能
"""

import logging
import os
import time
from functools import wraps
from typing import Callable, Any, Optional
from datetime import datetime

import config

class CrawlerException(Exception):
    """爬虫系统自定义异常基类"""
    pass

class WebDriverError(CrawlerException):
    """WebDriver相关异常"""
    pass

class PageLoadError(CrawlerException):
    """页面加载异常"""
    pass

class DataProcessError(CrawlerException):
    """数据处理异常"""
    pass

def setup_logging() -> None:
    """
    配置日志系统
    创建必要的日志目录和文件，设置日志格式和级别
    """
    # 创建日志目录
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )
    
    # 配置错误日志
    error_handler = logging.FileHandler(config.ERROR_LOG)
    error_handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(error_handler)

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称，通常使用模块名
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    return logging.getLogger(name)

def retry_on_exception(
    retries: int = config.RETRY_COUNT,
    delay: float = 1.0,
    exceptions: tuple = (Exception,),
    logger: Optional[logging.Logger] = None
) -> Callable:
    """
    异常重试装饰器
    
    Args:
        retries: 最大重试次数
        delay: 重试间隔（秒）
        exceptions: 需要重试的异常类型
        logger: 日志记录器实例
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < retries:
                        if logger:
                            logger.warning(
                                f"Function {func.__name__} failed with {str(e)}. "
                                f"Retrying {attempt + 1}/{retries}..."
                            )
                        time.sleep(delay * (attempt + 1))  # 指数退避
                    else:
                        if logger:
                            logger.error(
                                f"Function {func.__name__} failed after {retries} retries. "
                                f"Last error: {str(e)}"
                            )
                        raise last_exception
            return None
        return wrapper
    return decorator

def create_output_dirs() -> None:
    """
    创建必要的输出目录
    """
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

def get_timestamp() -> str:
    """
    获取当前时间戳字符串
    
    Returns:
        str: 格式化的时间戳字符串
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    # 替换Windows文件系统中的非法字符
    illegal_chars = '<>:"/\\|?*'
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def format_time_duration(seconds: float) -> str:
    """
    格式化时间持续时间
    
    Args:
        seconds: 持续时间（秒）
        
    Returns:
        str: 格式化的时间字符串
    """
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"