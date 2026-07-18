"""
归档模块

将生成的早报按日期归档到 archives/ 目录。
目录结构：archives/YYYY/MM/YYYY-MM-DD.md
"""

import os
from datetime import datetime, timezone, timedelta
from pathlib import Path


def get_archive_path(archive_dir: str, date_dt: datetime = None) -> Path:
    """
    获取归档文件的路径

    路径格式: archives/2025/07/2025-07-17.md
    """
    if date_dt is None:
        date_dt = datetime.now(timezone(timedelta(hours=8)))

    year = date_dt.strftime("%Y")
    month = date_dt.strftime("%m")
    date_str = date_dt.strftime("%Y-%m-%d")

    base = Path(archive_dir)
    path = base / year / month / f"{date_str}.md"
    return path


def save_brief(content: str, archive_dir: str = "archives",
               date_dt: datetime = None) -> str:
    """
    将早报内容保存到归档文件

    Args:
        content: 早报 Markdown 内容
        archive_dir: 归档根目录
        date_dt: 日期

    Returns:
        保存的文件路径
    """
    path = get_archive_path(archive_dir, date_dt)

    # 确保目录存在
    path.parent.mkdir(parents=True, exist_ok=True)

    # 写入文件（UTF-8）
    path.write_text(content, encoding="utf-8")

    return str(path)


def list_archives(archive_dir: str = "archives", limit: int = 10) -> list:
    """
    列出最近的归档文件

    Returns:
        文件路径列表（按日期降序）
    """
    base = Path(archive_dir)
    if not base.exists():
        return []

    md_files = sorted(base.rglob("*.md"), reverse=True)
    return [str(f) for f in md_files[:limit]]


def get_today_path(archive_dir: str = "archives") -> str:
    """获取今天的归档路径"""
    now = datetime.now(timezone(timedelta(hours=8)))
    return str(get_archive_path(archive_dir, now))
