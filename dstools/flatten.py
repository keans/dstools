def flatten_dict(y, key_filter=None, seperator="."):
    """
    flatten given dictionary, if filter is provided only given values are
    returned
    """
    res = {}

    def flatten(x, name="", seperator=""):
        if isinstance(x, dict):
            # --- dict ---
            for k in x.keys():
                flatten(x[k], "{}{}{}".format(name, k, seperator), seperator)

        elif isinstance(x, list):
            # --- list ---
            for no, k in enumerate(x):
                flatten(k, "{}{}{}".format(name, no, seperator), seperator)

        else:
            # --- value ---
            key = name[:-1]
            if (key_filter is None) or (key in key_filter):
                res[key] = x

    flatten(y, seperator=".")

    return res
