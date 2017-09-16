import itertools


def pairwise(iterable):
    """
    s -> (s0,s1), (s1,s2), (s2, s3), ...
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return list(zip(a, b))


def str2bool(v):
    """
    converts a string to a boolean
    """
    return v.lower() in ("yes", "true", "t", "1")


def chunks(li, size):
    """
    returns the given list in chunks of given size
    """
    for i in range(0, len(li), size):
        yield li[i:i+size]


def ngram(text, n=3):
    """
    return ngrams of the given text
    """
    for i in range(len(text) - n + 1):
        yield text[i:i+n]


def sizeof_fmt(no_bytes, unit=None, kibi=True):
    """
    returns a human friendly output of the given number of bytes
    in the given unit (or selecting an auto unit, if not provided)
    """
    units = list("kMGTPEZY")
    assert(not unit or (unit in units))

    if kibi:
        # kilo binary: 2**x
        base, suffix = (1024.0, "iB")
    else:
        # kilo: 10**x
        base, suffix = (1000.0, "B")

    if unit in units:
        # calculate size in the target unit
        no_bytes = no_bytes / (base ** (units.index(unit) + 1))

    else:
        # find a useful representation
        for no, unit in enumerate(units):
            if -base < no_bytes < base:
                unit = units[no - 1]
                break
            no_bytes /= base

    return "{:3.2f} {}{}".format(no_bytes, unit, suffix)
