from time import sleep
from typing import Any
from typing import Optional
from typing import Tuple
from typing import Type

from ytdl_sub.utils.logger import Logger

logger = Logger.get()


def retry(times: int, exceptions: Tuple[Type[Exception], ...], wait_sec: int = 5) -> Optional[Any]:
    """
    Retry decorator

    Parameters
    ----------
    times
        Number of attempts to retry
    exceptions
        Type of exceptions to retry against
    wait_sec
        Number of seconds to wait inbetween retries

    Returns
    -------
    Any or None
        If none, it implies all retries failed
    """

    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    logger.debug(
                        "Exception thrown when attempting to run %s, attempt %d of %d\n"
                        "Exception:\n%s",
                        func.__name__,
                        attempt + 1,
                        times,
                        str(exc),
                    )
                    attempt += 1
                    sleep(wait_sec)
            return None

        return newfn

    return decorator
