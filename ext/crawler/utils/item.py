from hashlib import md5

class Item(object):
    def __init__(self):
        self._values = {}
        for name in ['url', 'title', 'date', 'website', 'content', 'md5']:
            self._values[name] = None

    def __getitem__(self, key):
        if key=='md5' and self._values[key] == None:
            self._values[key] = md5((self._values['url']).encode('utf-8')).hexdigest()
        return self._values[key]

    def __setitem__(self, key, value):
        if key in self._values.keys():
            self._values[key] = value
        else:
            raise KeyError("%s does not support field: %s" %
                (self.__class__.__name__, key))

    def __delitem__(self, key):
        del self._values[key]

    def keys(self):
        return self._values.keys()

    def __dict__(self):
        assert self['md5'] != None
        return self._values