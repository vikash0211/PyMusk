
class TestCase:
    pass


class Hide(object):
    def __init__(self, condition):
        self.condition = condition

    def __call__(self, func):
        if self.condition:
            # Return the decorated function
            return None
        return func

def GoTo(func):
    from pyMusk import Data
    Data.goto = func

def get_duration(start, end):
    duration = end - start
    h = divmod(duration.total_seconds(), 3600)
    m = divmod(h[1], 60)
    s = m[1]
    hh = "%d"%h[0]
    hh = "0" + hh if len(hh) == 1 else hh
    mm = "%d"%m[0]
    mm = "0" + mm if len(mm) == 1 else mm
    ss = "%d"%s
    ss = "0" + ss if len(ss) == 1 else ss
    return "%s:%s:%s"%(hh, mm, ss)

