from Queue import Queue, Empty
from urllib2 import Request

class UrlQueue(object):

    def pop(self):
        raise NotImplemented

    def push(self):
        raise NotImplemented

class AtomQueue(UrlQueue):

    def __init__(self):
        self.queue = Queue()
        self.timeout = 10

    def pop(self):
        try:
            return self.queue.get(block=True, timeout=self.timeout)
        except Empty:
            return None

    def push(self, request):
        if not isinstance(request, Request):
            raise Exception('request must be urllib2.Request')
        self.queue.push(request)
