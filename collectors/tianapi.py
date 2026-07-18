"""
天行数据采集器（备用）

需要申请 API Key: https://www.tianapi.com/
接口: 新闻头条 (topnews)
"""

import json
import ssl
import urllib.request
import urllib.error
from typing import List

from .base import BaseCollector, NewsItem


class TianAPICollector(BaseCollector):
    """天行数据新闻采集器"""

    name = "tianapi"

    def __init__(self, api_key: str, api_url: str = "https://api.tianapi.com/topnews/index"):
        self.api_key = api_key
        self.api_url = api_url

    def fetch(self, count: int = 15) -> List[NewsItem]:
        """调用天行数据 API"""
        if not self.api_key:
            raise RuntimeError("天行数据 API Key 未配置，请在 config.py 中设置 TIANAPI_KEY")

        url = f"{self.api_url}?key={self.api_key}&num={count}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        ctx = ssl.create_default_context()

        try:
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"天行数据 API 请求失败: {e}")

        if data.get("code") != 200:
            raise RuntimeError(f"天行数据返回错误: {data.get('msg', '未知错误')}")

        result = []
        news_list = data.get("newslist", [])
        for i, item in enumerate(news_list, 1):
            news = NewsItem(
                title=item.get("title", ""),
                rank=i,
                summary=item.get("description", ""),
                source=item.get("source", "天行数据"),
                url=item.get("url", ""),
            )
            result.append(news)

        return result
