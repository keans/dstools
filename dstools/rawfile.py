from builtins import str

import os
import datetime
import gzip


class RawFile(object):
    """
    class to handle raw files, including auto naming after timestamps
    and splitting of files hitting the maximum MB size
    """
    def __init__(
        self, path, name, ext, prefix="", postfix="",
        max_size_mb=64, mode="wb", gzip=True
    ):
        self.path = path
        self.name = name
        self.ext = ext
        self.prefix = prefix
        self.postfix = postfix
        self.max_size_mb = max_size_mb
        self.gzip = gzip
        self.mode = mode

        self.reset()

    def reset(self, auto_reopen=True):
        """
        reset file by finalizing it (and reopen new file)
        """
        # create new start date
        self._f = None
        self.no = 0
        self.start_dt = datetime.datetime.now()
        self.end_dt = None
        self._filename = self._generate_filename()

        if auto_reopen:
            # reopen new file
            self.open()

    def finalize(self):
        """
        close open file, rename file by setting its end timestamp
        """
        # close open file
        self.close()

        # get old filename
        prev_filename = self.filename

        # set current date as end time
        self.end_dt = datetime.datetime.now()

        # get new filename
        self._filename = self._generate_filename()

        # rename file
        os.rename(prev_filename, self._filename)

    def open(self):
        """
        open internal file
        """
        if not self.gzip:
            # open normal file
            self._f = open(self.filename, self.mode)
        else:
            # open gzip file
            self._f = gzip.open(self.filename, self.mode)

    def close(self):
        """
        close internal file
        """
        if (self._f is not None) and (not self._f.closed):
            self._f.close()

    def write(self, content, flush=True, auto_split=True):
        """
        write content to file
        """
        if auto_split:
            if self.is_size_exceeded():
                # finalize existing file
                self.finalize()

                # reset file
                self.reset()

        self._f.write(content)
        if flush:
            self._f.flush()

    def is_size_exceeded(self):
        """
        returns true, if the current filesize exceeds or no limit set
        """
        current_size_mb = os.path.getsize(self.filename) / float(1024**2)
        return (
            (self.max_size_mb is None) or
            (current_size_mb > self.max_size_mb)
        )

    def _generate_filename(self):
        """
        return the current filename that is based on the start time,
        the end time, the prefix, the given name, the postfix and
        the file's extension
        """

        # start timestamp
        start_dt = self.start_dt.strftime("%Y%m%d%H%M")

        # end timestamp
        end_dt = "now"
        if self.end_dt is not None:
            end_dt = self.end_dt.strftime("%Y%m%d%H%M")

        # base name
        name = ""
        if self.prefix != "":
            name += "%s_" % self.prefix
        name += str(self.name)
        if self.postfix != "":
            name += "_%s" % self.postfix

        # get non-existing filename
        filename = None
        while True:
            filename = os.path.join(
                os.path.abspath(self.path),
                "%s_%s_%s_%03d.%s" % (
                    start_dt, end_dt, name, self.no, self.ext
                )
            )
            if not os.path.exists(filename):
                return filename

            self.no += 1

    @property
    def filename(self):
        return self._filename

    def __str__(self):
        return self.filename
