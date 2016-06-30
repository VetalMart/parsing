import time
#from timeit import verbose

class Timer(object):
    def __init__(self, verbose=False):
        self.__verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.__verbose:
            print('elapsed time: %f ms')% self.msecs
