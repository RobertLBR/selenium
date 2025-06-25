#!/usr/bin/env python3
import argparse
import logging
from importlib.metadata import entry_points
from typing import List, Dict, Any
import requests
from src.plugin_base import PluginBase

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self):
        # 加载所有注册的插件
        self.input_plugins = self._load_plugins('web_crawler.input_plugins')
        self.parse_plugins = self._load_plugins('web_crawler.parse_plugins')
        self.api_plugins = self._load_plugins('web_crawler.api_plugins')

    def _load_plugins(self, group: str) -> List[PluginBase]:
        """加载指定类型的插件"""
        plugins = []
        for entry in entry_points().get(group, []):
            try:
                plugin_class = entry.load()
                plugins.append(plugin_class())
                logger.info(f"成功加载插件: {entry.name}")
            except Exception as e:
                logger.error(f"加载插件 {entry.name} 失败: {str(e)}")
        return plugins

    def crawl(self, url: str) -> Dict[str, Any]:
        """执行完整的爬取流程"""
        result = {'url': url, 'steps': []}
        
        try:
            # 1. 输入层处理
            request = {'url': url}
            for plugin in self.input_plugins:
                if plugin.can_handle(url):
                    request = plugin.process_request(request)
                    result['steps'].append(f"输入处理: {plugin.__class__.__name__}")
                    break
            
            # 2. 获取网页内容
            response = requests.get(
                request['url'],
                headers=request.get('headers', {})
            )
            response.raise_for_status()
            result['steps'].append("获取网页内容成功")
            
            # 3. 解析层处理
            content = response.text
            for plugin in self.parse_plugins:
                if plugin.can_handle(url):
                    parsed = plugin.parse(content)
                    result.update(parsed)
                    result['steps'].append(f"内容解析: {plugin.__class__.__name__}")
                    break
            
            # 4. API层处理 (可选)
            for plugin in self.api_plugins:
                if plugin.can_handle(url):
                    api_result = plugin.call_api(result)
                    result['api_result'] = api_result
                    result['steps'].append(f"API调用: {plugin.__class__.__name__}")
                    break
            
            result['status'] = 'success'
        except Exception as e:
            logger.error(f"爬取过程中出错: {str(e)}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='网页爬虫命令行工具')
    parser.add_argument('cli', help='启动命令行模式')
    parser.add_argument('url', help='要爬取的URL')
    args = parser.parse_args()

    # 创建爬虫实例并执行
    crawler = WebCrawler()
    result = crawler.crawl(args.url)
    
    # 输出结果
    print("\n爬取结果:")
    print(f"URL: {result['url']}")
    print(f"状态: {result['status']}")
    if result['status'] == 'success':
        print("处理步骤:")
        for step in result['steps']:
            print(f" - {step}")
        if 'title' in result:
            print(f"\n标题: {result['title']}")
        if 'content' in result:
            print(f"\n内容摘要: {result['content'][:200]}...")
    else:
        print(f"错误: {result['error']}")

if __name__ == '__main__':
    main()