import functools
import traceback

from personal_spotted_alert.log import log


def safe(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            log('%s crashed:\n%s' % (func.__name__, traceback.format_exc()))

    return wrapper
