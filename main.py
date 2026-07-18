#!/usr/bin/env python3
"""
Daily News Digest — 每日新闻早报

采集新闻 → 格式化早报 → 归档存储

用法:
    python main.py                        # 生成今天的早报
    python main.py --date 2025-07-17      # 重新生成指定日期
    python main.py --count 15             # 自定义新闻条数
    python main.py --dry                  # 只打印，不归档
    python main.py --no-emoji             # 不使用 emoji
"""

import sys
import os
from datetime import datetime, timezone, timedelta

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from collectors import BaiduHotCollector
from formatter import format_brief
from archiver import save_brief
from config import NEWS_COUNT, ARCHIVE_DIR, BRIEF_NAME

USAGE = """\
每日新闻早报 — Daily News Digest

用法:
  python main.py                        生成今天的早报（12条新闻）
  python main.py --date YYYY-MM-DD      生成指定日期的早报
  python main.py --count N              自定义新闻条数（默认 12）
  python main.py --dry                  预览模式（不归档）
  python main.py --no-emoji             不使用 emoji

示例:
  python main.py
  python main.py --dry --count 15
  python main.py --date 2026-07-17
"""


def parse_args():
    args = {
        "date": None,
        "count": NEWS_COUNT,
        "dry": False,
        "no_emoji": False,
    }

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ("--help", "-h"):
            print(USAGE)
            sys.exit(0)
        elif arg == "--date" and i + 1 < len(sys.argv):
            args["date"] = sys.argv[i + 1]
            i += 2
        elif arg == "--count" and i + 1 < len(sys.argv):
            try:
                args["count"] = int(sys.argv[i + 1])
            except ValueError:
                print(f"错误: --count 需要数字，收到 '{sys.argv[i+1]}'")
                sys.exit(1)
            i += 2
        elif arg == "--dry":
            args["dry"] = True
            i += 1
        elif arg == "--no-emoji":
            args["no_emoji"] = True
            i += 1
        else:
            print(f"未知参数: {arg}")
            print(USAGE)
            sys.exit(1)

    return args


def get_date(date_str: str = None) -> datetime:
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").replace(
                tzinfo=timezone(timedelta(hours=8))
            )
        except ValueError:
            print(f"错误: 日期格式无效 '{date_str}'，应为 YYYY-MM-DD")
            sys.exit(1)
    return datetime.now(timezone(timedelta(hours=8)))


def main():
    args = parse_args()
    date_dt = get_date(args["date"])
    count = args["count"]
    is_dry = args["dry"]

    # ── 1. 采集新闻 ──────────────────────────────────
    print(f"📡 正在采集新闻...（来源: 百度热搜）")

    try:
        collector = BaiduHotCollector()
        news_items = collector.fetch(count=count * 2)
    except RuntimeError as e:
        print(f"❌ 采集失败: {e}")
        sys.exit(1)

    if not news_items:
        print("❌ 未获取到新闻")
        sys.exit(1)

    print(f"✅ 获取到 {len(news_items)} 条新闻")

    # ── 2. 格式化早报 ──────────────────────────────────
    print("📝 正在生成早报...")

    brief_text = format_brief(
        news_items=news_items,
        count=count,
        brief_name=BRIEF_NAME,
        date_dt=date_dt,
    )

    print(brief_text)

    # ── 3. 归档 ──────────────────────────────────────
    if is_dry:
        print("\n[干运行模式] 未保存文件")
    else:
        filepath = save_brief(brief_text, ARCHIVE_DIR, date_dt)
        print(f"\n💾 已归档: {filepath}")

    print("\n✅ 完成！")


if __name__ == "__main__":
    main()
