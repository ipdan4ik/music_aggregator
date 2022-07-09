import functools
import time

from loguru import logger
from requests.exceptions import HTTPError, ConnectionError
MAX_REQUEST_RETRIES = 10


def request_reconnect(func):
    """ Decorator for reconnecting to request on failure """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        retries = 0
        is_success = False
        while retries < MAX_REQUEST_RETRIES and not is_success:
            try:
                return func(*args, **kwargs)
            except(
                HTTPError,
                ConnectionError
            ) as err:
                retries += 1
                print(f'Request error: {err}\nTrying again ({retries**2}s)..')
                time.sleep(retries**2)
    return wrapper


def performance_timing(func):
    """ Decorator for logging performance of function """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        time0 = time.time()
        logger.info(f'Started {func.__name__!r}')
        response = func(*args, **kwargs)
        logger.info(f'Finished {func.__name__!r} in {time.time() - time0} s.')
        return response
    return wrapper
