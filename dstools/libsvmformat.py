import csv
import codecs
import collections


class LibSvmFormatRow(object):
    """
    representation of a single row in a libsvm format file, consisting out of
    <label> <index1>:<value1> <index2>:<value2> ... <indexn>:<valuen>
    """
    def __init__(self, label, features, comment=""):
        self.label = label
        self.features = features
        self.comment = comment

    def __getitem__(self, no):
        return self.features.get(no)

    def __setitem__(self, no, value):
        self.features[no] = value

    @property
    def values(self):
        return list(self.features.values())

    @property
    def indices(self):
        return list(self.features.keys())

    def __repr__(self):
        return "<LibSvmFormatRow(label='%s', features=[%s], comment='%s')>" % (
            self.label,
            ", ".join([
                "%s:%s" % (k, v)
                for k, v in list(self.features.items())
            ]),
            self.comment
        )

    def __str__(self):
        return "%s %s%s" % (
            self.label,
            self.features,
            " %s" % self.comment if self.comment != "" else ""
        )


class LibSvmFormatFile(object):
    """
    representation of a libsvm formatted file that is consisting out of
    LibSvmFormatRow rows
    """
    def __init__(self, filename, encoding="utf-8"):
        self.filename = filename
        self.encoding = encoding

    def readrows(self):
        """
        generator that returns libsvm formatted rows in a row-wise fashion
        """
        with codecs.open(self.filename, "r", self.encoding) as f:
            for line in f:
                # make row unicode
                row = [x.encode("utf8") for x in line.split(" ")]

                # get label from first column
                label = row.pop(0)

                try:
                    # get comment starting at first appearance of '#'
                    i = row.index("#")
                    comment = " ".join(row[i+1:]).strip()

                    # just keep cols before the comment for features
                    row = row[:i-1]

                except ValueError:
                    # just ignore missing comments
                    comment = None

                # split all features by : and put them to an ordered dict
                row = [x.split(":") for x in row]
                features = collections.OrderedDict(
                    (int(x[0]), float(x[1]))
                    for feat in row
                )

                # prepare libsvm format row for simpler handling of data
                libsvm_row = LibSvmFormatRow(
                    label=label,
                    features=features,
                    comment=comment
                )

                yield libsvm_row


class LibSvmPredFile(object):
    """
    representation of a libsvm prediction file
    """
    def __init__(self, filename, encoding="utf-8"):
        self.filename = filename
        self.encoding = encoding

    def readrows(self):
        """
        generator that returns libsvm formatted rows in a row-wise fashion
        """
        with codecs.open(self.filename, "r", self.encoding) as f:
            reader = csv.reader(f, dialect="libsvmpred")
            for row in reader:
                # get label from first column
                yield int(row[0]), float(row[1])
