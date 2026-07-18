"""
新闻采集器基类

所有数据源采集器继承 BaseCollector，实现 fetch() 方法。
统一返回 NewsItem 列表。
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class NewsItem:
    """统一的新闻条目"""
    title: str                             # 新闻标题
    rank: int = 0                          # 排名（1-based）
    summary: str = ""                      # 简短描述
    source: str = ""                       # 来源
    url: str = ""                          # 原文链接
    hot_score: Optional[int] = None        # 热度分数

    def to_short(self, max_len: int = 60) -> str:
        """转为一行的简略格式"""
        t = self.title.strip()
        if len(t) > max_len:
            t = t[:max_len - 1] + "…"
        return t


class BaseCollector:
    """采集器基类"""

    name = "base"

    def fetch(self, count: int = 15) -> List[NewsItem]:
        """获取新闻列表，返回 NewsItem 列表"""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<Collector: {self.name}>"
