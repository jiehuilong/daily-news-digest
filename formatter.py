"""
早报格式化器

将新闻列表格式化为「匡扶会早报」风格的 Markdown 文本。
"""

from datetime import datetime, timezone, timedelta
from typing import List

from collectors.base import NewsItem

# ════════════════════════════════════════════════════════
# 星期映射
# ════════════════════════════════════════════════════════
WEEKDAYS_CN = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

# ════════════════════════════════════════════════════════
# 农历数据表（2024-2034）
# 每项: (春节公历月, 春节公历日, 月天数编码)
# 月天数编码: bit 0=正月(0小29/1大30) … bit 11=腊月
# 闰月信息: 0=无闰月, 否则 (闰月月份, 闰月天数0=29/1=30)
# ════════════════════════════════════════════════════════
LUNAR_TABLE = {
    2024: (2, 10,  0x1b5ac, None),
    2025: (1, 29,  0x1b5ad, (6, 30)),     # 闰六月 30天
    2026: (2, 17,  0x1d5a6, None),
    2027: (2, 6,   0x1adaa, None),
    2028: (1, 26,  0x1d6a6, None),
    2029: (2, 13,  0x1adaa, None),
    2030: (2, 3,   0x1dd6c, (7, 30)),     # 闰七月 30天
    2031: (1, 23,  0x1adaa, None),
    2032: (2, 11,  0x1dd6c, (6, 30)),     # 闰六月 30天
    2033: (1, 31,  0x1ab6a, (11, 30)),    # 闰十一月 30天
    2034: (2, 19,  0x1b5ac, None),
}

MONTHS_CN = ["正", "二", "三", "四", "五", "六",
             "七", "八", "九", "十", "冬", "腊"]
DAYS_CN = ["", "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
           "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
           "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]

TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
SHENGXIAO = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]


def get_beijing_time() -> datetime:
    """获取当前北京时间"""
    return datetime.now(timezone(timedelta(hours=8)))


def solar_to_lunar(year: int, month: int, day: int) -> (int, int, int):
    """
    公历转农历

    Returns:
        (lunar_year, lunar_month, lunar_day)
        失败时返回 None
    """
    # 查找农历年数据
    info = LUNAR_TABLE.get(year)
    if not info:
        # 尝试前一年（春节前的日期属于前一个农历年）
        info = LUNAR_TABLE.get(year - 1)
        if not info:
            return None

    spring_m, spring_d, days_enc, leap = info

    # 构建公历春节日期
    import calendar
    spring_date = datetime(year, spring_m, spring_d)
    target_date = datetime(year, month, day)

    # 如果目标日期在春节前，属于上一个农历年
    if target_date < spring_date:
        return solar_to_lunar(year - 1, month, day)

    days_since_spring = (target_date - spring_date).days

    # 解析各月天数
    month_days = []
    for i in range(12):
        if (days_enc >> i) & 0x1:
            month_days.append(30)
        else:
            month_days.append(29)

    # 如果有闰月，插入到月份序列中
    lunar_months = []
    if leap:
        leap_month, leap_days = leap
        # 插入闰月
        for i in range(12):
            lunar_months.append((i + 1, month_days[i], False))
            if i + 1 == leap_month:
                lunar_months.append((leap_month, leap_days, True))
    else:
        for i in range(12):
            lunar_months.append((i + 1, month_days[i], False))

    remaining = days_since_spring
    for m, md, is_leap in lunar_months:
        if remaining < md:
            return (year, m, remaining + 1, is_leap)
        remaining -= md

    # 超出范围
    return None


def format_lunar_date(dt: datetime) -> str:
    """格式化农历日期字符串"""
    result = solar_to_lunar(dt.year, dt.month, dt.day)
    if result is None:
        return ""

    year, l_month, l_day, is_leap = result

    # 年柱（天干地支）
    gan = TIANGAN[(year - 4) % 10]
    zhi = DIZHI[(year - 4) % 12]
    sx = SHENGXIAO[(year - 4) % 12]

    month_str = MONTHS_CN[l_month - 1]
    day_str = DAYS_CN[l_day] if l_day < len(DAYS_CN) else str(l_day)

    prefix = "闰" if is_leap else ""

    return f"{gan}{zhi}年【{sx}年】农历{prefix}{month_str}月{day_str}"


def format_brief(news_items: List[NewsItem],
                 count: int = 12,
                 brief_name: str = "每日新闻",
                 date_dt: datetime = None) -> str:
    """
    将新闻列表格式化为早报 Markdown 文本

    输出格式类似匡扶会早报：
    ━━━━━━━━━━━━━━━━━━━━━━━━━
    每日新闻早报☀️

    7月18日，星期六，乙巳年【蛇年】农历六月初五

    1、新闻标题...
    2、新闻标题...
    ...

    【微语】人生最好的状态：眼里有光，心中有爱，脚下有路，未来可期。
    ━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    if date_dt is None:
        date_dt = get_beijing_time()

    month = date_dt.month
    day = date_dt.day
    weekday = WEEKDAYS_CN[date_dt.weekday()]

    # 农历日期
    try:
        lunar_str = format_lunar_date(date_dt)
    except Exception:
        lunar_str = ""

    # 天气 emoji
    sun_emojis = ["☀️", "🌤️", "☀️", "🌅"]

    lines = []
    sep = "━" * 30
    lines.append(sep)
    lines.append("")
    title = f"{brief_name}早报{sun_emojis[0]}"
    lines.append(title)
    lines.append("")
    lines.append(f"{month}月{day}日，{weekday}，{lunar_str}")
    lines.append("")

    # 新闻列表
    selected = news_items[:count]
    for i, item in enumerate(selected, 1):
        title_text = item.title.strip()
        if item.summary:
            summary = item.summary.strip()
            if summary and summary != title_text and len(summary) < 100:
                lines.append(f"{i}、{title_text}。{summary}")
            else:
                lines.append(f"{i}、{title_text}")
        else:
            lines.append(f"{i}、{title_text}")

    lines.append("")
    lines.append("【微语】人生最好的状态：眼里有光，心中有爱，脚下有路，未来可期。")
    lines.append("")
    lines.append(f"📅 数据来源：百度热搜实时榜 | {date_dt.strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append(sep)

    return "\n".join(lines)
