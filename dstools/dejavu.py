import os
import collections


class DejaVu:
    """
    class to keep track of already seen items
    """
    def __init__(self):
        self._unique_items = set()

    def seen(self, item):
        """
        returns True, if the given item was already seen
        """
        if item in self._unique_items:
            # existing item
            return True

        # add new item to set
        self._unique_items.add(item)

        return False

    def reset(self):
        """
        reset all seen items
        """
        self._unique_items = set()

    def __str__(self):
        return "{}".format(self._unique_items)


class PersistentDejaVu:
    """
    extends the DejaVu class to support persistence
    by using a simple text file
    """
    def __init__(self, filename, autoload=True):
        DejaVu.__init__(self)

        self._filename = filename
        if autoload is True:
            # load stored items
            self.load()

    def seen(self, item):
        """
        returns True, if the given item was already seen;
        if seen for the first time, append it to the text file
        """
        is_existing = DejaVu.seen(self, item)
        if is_existing is False:
            self._append(item)

        return is_existing

    def _append(self, item):
        with open(self._filename, "a") as f:
            f.write("{}\n".format(item))

    def reset(self):
        """
        reset all seen items and remove stored items
        """
        DejaVu.reset(self)
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
        self._unique_items = collections.defaultdict(set)

    def seen(self, key, item):
        """
        returns True, if the given item was already seen for
        the given key
        """
        if item in self._unique_items[key]:
            # existing item
            return True

        # add new item to set
        self._unique_items[key].add(item)

        return False

    def reset(self):
        """
        reset all seen items
        """
        self._unique_items = collections.defaultdict(set)

    def __str__(self):
        tmp = ""
        for k, v in self._unique_items.items():
            tmp += "----- {} -----\n{}\n".format(
                k, v
            )

        return tmp
