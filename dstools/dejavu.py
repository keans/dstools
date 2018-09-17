import os
import collections
import threading


class DejaVu:
    """
    class to keep track of already seen items
    """
    def __init__(self):
        self._lock = threading.RLock()
        self._unique_items = set()

    def seen(self, item, auto_append=True):
        """
        returns True, if the given item was already seen
        """
        if item in self._unique_items:
            # existing item
            return True

        if auto_append is True:
            # add new item to set
            self.append(item)

        return False

    def append(self, item):
        """
        append an item to unique items list
        """
        with self._lock:
            self._unique_items.add(item)

    def reset(self):
        """
        reset all seen items
        """
        with self._lock:
            self._unique_items.clear()

    def __str__(self):
        return "{}".format(self._unique_items)


class PersistentDejaVu(DejaVu):
    """
    extends the DejaVu class to support persistence
    by using a simple text file
    """
    def __init__(self, filename, auto_load=True):
        DejaVu.__init__(self)

        self._filename = filename
        if auto_load is True:
            # load stored items
            self.load()

    def seen(self, item, auto_append=True):
        """
        returns True, if the given item was already seen;
        if seen for the first time, append it to the text file
        """
        is_existing = DejaVu.seen(self, item)
        if (is_existing is False) and (auto_append is True):
            self.append(item)

        return is_existing

    def append(self, item):
        """
        append item to persistent already seen file
        """
        DejaVu.append(self, item)
        with self._lock:
            with open(self._filename, "a") as f:
                f.write("{}\n".format(item))

    def reset(self):
        """
        reset all seen items and remove stored items
        """
        DejaVu.reset(self)
        with self._lock:
            if os.path.exists(self._filename):
                os.remove(self._filename)

    def load(self):
        """
        load all existing items from file
        """
        if os.path.exists(self._filename):
            with open(self._filename, "r") as f:
                self._unique_items = set([
                    line.strip()
                    for line in f.read().splitlines()
                ])


class DejaVuMultiple:
    """
    class to keep track of already seen items for
    multiple keys
    """
    def __init__(self):
        self._lock = threading.RLock()
        self._unique_items = collections.defaultdict(set)

    def seen(self, key, item, auto_append=True):
        """
        returns True, if the given item was already seen for
        the given key
        """
        if item in self._unique_items[key]:
            # existing item
            return True

        if auto_append is True:
            self.append(key, item)

        return False

    def append(self, key, item):
        """
        append item to persistent already seen file
        """
        with self._lock:
            # add new item to set
            self._unique_items[key].add(item)

    def reset(self):
        """
        reset all seen items
        """
        with self._lock:
            self._unique_items.clear()

    def __str__(self):
        tmp = ""
        for k, v in self._unique_items.items():
            tmp += "----- {} -----\n{}\n".format(
                k, v
            )

        return tmp
