from threading import RLock
from collections import defaultdict


class _StorageDataContextManager(object):

    lock = None
    data = None

    def __init__(self, data):
        self.data = data
        self.lock = RLock()

    def __enter__(self):
        self.lock.acquire()
        return self.data

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.lock.release()


class Storage(object):
    """Implements a thread-safe storage object.

    Usage:
    storage = Storage(factory_method)
    with storage(key) as locked_data:
        locked_data.somemethod()
    """

    _storage = None

    g_lock = None

    def __init__(self, storage_obj_creator):
        self.g_lock = RLock()

        def new_context():
            return _StorageDataContextManager(storage_obj_creator())

        self._storage = defaultdict(new_context)

    def __call__(self, key):
        self.g_lock.acquire()
        manager = self._storage[key]
        self.g_lock.release()
        return manager
