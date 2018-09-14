def flatten_dict(y, key_filter=None):
    """
    flatten given dictionary, if filter is provided only given values are
    returned
    """
    res = {}

    def flatten(x, name=''):
        if isinstance(x, dict):
            # --- dict ---
            for k in x.keys():
                flatten(x[k], "{}{}_".format(name, k))

        elif isinstance(x, list):
            # --- list ---
            for no, k in enumerate(x):
                flatten(k, "{}{}_".format(name, no))

        else:
            # --- value ---
            key = name[:-1]
            if (key_filter is None) or (key in key_filter):
                res[key] = x

    flatten(y)

    return res
