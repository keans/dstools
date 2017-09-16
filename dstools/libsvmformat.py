import re
import collections
import operator

import numpy as np
import scipy.sparse as sp

from .osutils import get_linewise

# some helper functions for easy access to the libsvmformat
#
# <label> <index1>:<value1> <index2>:<value2> ... <indexn>:<valuen> # comment
#


def create_libsvmline(label, features, comment=None):
    """
    creates a libsvm format line with provided label (integer),
    the sorted dictionary of features and an optional comment
    """
    assert(isinstance(label, int))
    assert(isinstance(features, collections.OrderedDict))

    # prepare features dict as string
    features_str = " ".join(
        "%d:%g" % (no + 1, v)
        for no, v in enumerate(features.values())
        if v != 0
    )

    if comment is not None:
        # return libsvm line with comment
        return "%d %s # %s\n" % (label, features_str, comment)

    # return libsvm line without comment
    return "%d %s\n" % (label, features_str)


def parse_libsvm_format(line):
    """
    parse a line from a libsvm format file and
    split it into label, features and optional comment
    """
    # use regex to obtain label and comment

    res = line.split("#", 1)

    label, features = res[0].split(" ", 1)
    comment = res[1].strip() if len(res) == 2 else None

    # use regex to obtain all features from the given line and
    # parse them to feature_no (int) and value (float) and sort them
    features = collections.OrderedDict(
        sorted([
            (int(feat[0]), float(feat[1]))
            for feat in re.compile(
                r"(\d+):([+-]?([0-9]*[.])?[0-9]+)+"
            ).findall(features)
        ], key=operator.itemgetter(0))
    )

    return int(label), features, comment


def get_libsvm_format(libsvmfile):
    """
    returns the parsed libsvm format file
    """
    # read labels, features and comments from libsvm file
    labels, features, comments = list(zip(
        *get_linewise(libsvmfile, parse_libsvm_format)
    ))

    # prepare sparse features matrix X
    rows, cols, vals = [], [], []
    for no, row in enumerate(features):
        for k, v in list(row.items()):
            rows.append(no)
            cols.append(k)
            vals.append(v)
    X = sp.csr_matrix((vals, (rows, cols)))

    # prepare labels array
    y = np.array(labels, "i")

    return y, X, comments


def parse_libsvm_pred_format(line):
    """
    parse a line from a libsvm pred file and
    split it into predicted label and score
    """
    parts = line.split(",")
    return (
        (int(parts[0]), float(parts[1]) if len(parts) == 2 else np.nan)
    )


def get_libsvm_pred(libsvmfile):
    """
    returns the predicted labels and scores from the parsed libsvm pred file
    """
    pred_labels, pred_scores = list(zip(
        *get_linewise(libsvmfile, parse_libsvm_pred_format)
    ))

    return np.array(pred_labels, "i"), np.array(pred_scores, "f")


def zip_features(features, feature_names):
    """
    simply zips the features obtained by parsing a libsvm file i.e.
    an ordered dict of (feature_no, value) pairs with a list of
    feature names
    """
    return collections.OrderedDict(
        (feature_names[feat - 1], features[feat])
        for feat in list(features.keys())
    )
