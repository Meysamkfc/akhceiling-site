# -*- coding: utf-8 -*-
"""Gregorian -> Jalali (Persian) calendar, no external dependency."""
from datetime import datetime


def g2j(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31
        jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30
        jd = 1 + (days - 186) % 30
    return jy, jm, jd


def _fa(s):
    return str(s).translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹'))


def jdate(value):
    """'2026-10-17 12:30:00' / datetime -> '۱۴۰۵/۰۷/۲۵'"""
    d = _parse(value)
    if not d:
        return ''
    y, m, dd = g2j(d.year, d.month, d.day)
    return _fa('%04d/%02d/%02d' % (y, m, dd))


def jdatetime(value):
    d = _parse(value)
    if not d:
        return ''
    return jdate(d) + ' ' + _fa(d.strftime('%H:%M'))


def jyear(value=None):
    d = _parse(value) or datetime.now()
    return g2j(d.year, d.month, d.day)[0]


def _parse(v):
    if isinstance(v, datetime):
        return v
    if not v:
        return None
    try:
        return datetime.strptime(str(v)[:19], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            return datetime.strptime(str(v)[:10], '%Y-%m-%d')
        except ValueError:
            return None
