from loach.utils import retry
from queue import Queue
from loach.utils.exception import *


def f(kwargs):
    a = kwargs
    a["new"] = 'new'

d = {
    "1":1,
    "2":2
}
f(d)
print(d)