"""
Daily News Digest — 配置文件
"""

# ── 基础设置 ──────────────────────────────────────────
NEWS_COUNT = 12          # 每期早报新闻条数
ARCHIVE_DIR = "archives" # 归档目录（相对路径或绝对路径）

# ── 数据源设置 ──────────────────────────────────────
# 默认使用百度热搜（无需 API Key）
# 如需切换数据源，修改 SOURCE 为对应采集器名称
SOURCE = "baidu_hot"

# 备用数据源 — 天行数据（需注册获取 Key）
# https://www.tianapi.com/  →  申请「新闻头条」接口
TIANAPI_KEY = ""
TIANAPI_URL = "https://api.tianapi.com/topnews/index"

# ── 输出格式 ──────────────────────────────────────────
# 早报标题模板
BRIEF_TITLE_TEMPLATE = "{name}早报{sun}"

# 早报名号（默认"匡扶会"，可修改）
BRIEF_NAME = "每日新闻"

# 日期格式
DATE_FORMAT_CHINESE = "%Y年%m月%d日"

# ── 推送设置（预留） ────────────────────────────────
# Telegram Bot (预留)
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""

# SMTP 邮件 (预留)
SMTP_HOST = ""
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASSWORD = ""
SMTP_TO = ""
