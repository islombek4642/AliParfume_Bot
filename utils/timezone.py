import datetime
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

TZ_UZBEKISTAN = zoneinfo.ZoneInfo("Asia/Tashkent")

def get_now() -> datetime.datetime:
    """Returns the current time in Uzbekistan as a native datetime object."""
    return datetime.datetime.now(TZ_UZBEKISTAN).replace(tzinfo=None)

def get_now_aware() -> datetime.datetime:
    """Returns the current time in Uzbekistan as a timezone-aware datetime object."""
    return datetime.datetime.now(TZ_UZBEKISTAN)
