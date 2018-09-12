# -*- coding: utf-8 -*-
import time
from functools import wraps
import traceback
import logging

import sys

error_print = True
error_trace = True
logger = logging.getLogger('loach')


def retry(times=3, forever=False):
    def decorate(func):
        @wraps(func)
        def retryed(*args, **kwargs):
            i = 0
            while forever or i < times+1:
                try:
                    return func(*args, times=i, **kwargs)
                except Exception as e:
                    i = i + 1
                    time.sleep(5)
                    if error_print:
                        # print(e)
                        logger.debug(e)
                        logger.debug("第 %d 次重试。[msg]: %s" % (i, e.msg))
                        # print("第 %d 次重试。[msg]: %s" % (i, e.msg))
                    if error_trace:
                        my_print_exe()

        return retryed
    return decorate


def dict_trip(d):
    keys = [k for k in d.keys()]
    for k in keys:
        if not d[k]:
            d.pop(k)


def my_print_exe():
    print_exc()


def print_exc(limit=None, file=None, chain=True):
    """Shorthand for 'print_exception(*sys.exc_info(), limit, file)'."""
    print_exception(*sys.exc_info(), limit=limit, file=file, chain=chain)


def print_exception(etype, value, tb, limit=None, file=None, chain=True):
    """Print exception up to 'limit' stack trace entries from 'tb' to 'file'.

    This differs from print_tb() in the following ways: (1) if
    traceback is not None, it prints a header "Traceback (most recent
    call last):"; (2) it prints the exception type and value after the
    stack trace; (3) if type is SyntaxError and value has the
    appropriate format, it prints the line where the syntax error
    occurred with a caret on the next line indicating the approximate
    position of the error.
    """
    # format_exception has ignored etype for some time, and code such as cgitb
    # passes in bogus values as a result. For compatibility with such code we
    # ignore it here (rather than in the new TracebackException API).
    if file is None:
        file = sys.stderr
    for line in traceback.TracebackException(
            type(value), value, tb, limit=limit).format(chain=chain):
        logger.debug(line)