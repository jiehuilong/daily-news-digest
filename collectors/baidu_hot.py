"""
百度热搜采集器

调用百度热搜 API（无需 API Key），实时获取中文热搜新闻。
API 接口: https://top.baidu.com/api/board?tab=realtime
"""

import json
import ssl
import urllib.request
import urllib.error
from typing import List

from .base import BaseCollector, NewsItem


class BaiduHotCollector(BaseCollector):
    """百度热搜采集器"""

    name = "baidu_hot"
    api_url = "https://top.baidu.com/api/board?tab=realtime"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    def fetch(self, count: int = 15) -> List[NewsItem]:
        """从百度热搜获取新闻"""
        items = self._request_api(count)
        return items

    def _request_api(self, count: int) -> List[NewsItem]:
        """请求百度热搜 API 并解析"""
        req = urllib.request.Request(
            self.api_url,
            headers={"User-Agent": self.user_agent},
        )

        ctx = ssl.create_default_context()

        try:
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"百度热搜 API 请求失败: {e}")

        # 解析返回结构
        try:
            cards = data["data"]["cards"]
            hot_list = None
            for card in cards:
                if card.get("component") == "hotList":
                    hot_list = card["content"]
                    break
            if hot_list is None:
                raise ValueError("未找到 hotList 数据")
        except (KeyError, IndexError, TypeError) as e:
            raise RuntimeError(f"百度热搜数据解析失败: {e}")

        result = []
        for i, item in enumerate(hot_list[:count], 1):
            news = NewsItem(
                title=item.get("word", ""),
                rank=i,
                summary=item.get("desc", ""),
                source="百度热搜",
                url=item.get("appUrl", ""),
                hot_score=item.get("hotScore"),
            )
            result.append(news)

        return result
