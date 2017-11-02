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

    def __str__(self):
        return "{}".format(self._unique_items)


class DejaVuMultiple:
    """
    class to keep track of already seen items for
    multiple keys
    """
    def __init__(self):
        self._unique_items = collections.defaultdict(set)

    def already_seen(self, key, item):
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

    def __str__(self):
        tmp = ""
        for k, v in self._unique_items.items():
            tmp += "----- {} -----\n{}\n".format(
                k, v
            )

        return tmp
