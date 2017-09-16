import os
import sys
import gzip
import io
import glob
import codecs
import collections
import bz2

try:
    import ujson as json
except:
    import json


# ----------- path ----------
def get_path_or_create(path):
    """
    returns the path and the flag, if it has been just created
    """
    if not os.path.exists(path):
        os.makedirs(path)
        return path, True

    return path, False


def get_dir_or_error(path):
    """
    returns the path or exists with an error, if it is not existing
    """
    if not os.path.exist(path):
        sys.exit("The path '%s' does not exist. Abort!" % path)

    return path


def add_file_directory_to_path(f, rel_path=".."):
    """
    get the directory of the given path, joins it with the
    given rel_path and adds it to the path
    (normally just the __file__ of the calling module is provided)
    """

    path = os.path.abspath(
        os.path.join(os.path.dirname(f), rel_path)
    )
    if not os.path.exists(path):
        sys.exit(
            "The path '%s' does not exist and thus cannot "
            "be added to the PATH variable. Abort!" % path
        )

    if path not in sys.path:
        sys.path.append(path)


def disk_free(path, relative=True):
    """
    returns the total size, the used size and the free size of the
    provided disk. If relative is true, the percentage is returned
    """
    st = os.statvfs(path)
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    free = st.f_bavail * st.f_frsize

    if relative:
        # calculate percent
        used = (used / float(total)) * 100
        free = (free / float(total)) * 100
        total = 100.0

    return collections.namedtuple(
        "DiskFree", "total used free"
    )(total, used, free)


# ---------- file -----------
def get_filename_or_error(filename, paths=[]):
    """
    tries to find the given filename in one of the paths in given order.
    If it exists the filename including the path will be returned,
    otherwise an error is raised
    """
    if filename is None:
        sys.exit("No filename provided! Abort.")

    if "./" not in paths:
        # always add current directory as path
        paths.insert(0, "./")

    # check provided paths for matching file
    for path in paths:
        p = os.path.abspath(os.path.join(path, filename))
        if os.path.exists(p) and os.path.isfile(p):
            return p

    if paths == ["./"]:
        sys.exit("The file '%s' does not exist! Abort." % filename)

    else:
        sys.exit(
            "The file '%s' does not exist in the paths %s! Abort." % (
                filename, str(paths)
            )
        )


def open_read(filename):
    """
    open file depending on extension
    """
    _, ext = os.path.splitext(filename)
    if ext == ".gz":
        # open as gzip
        return gzip.open(filename, "rb")
    elif ext == ".bz2":
        # open as bz2
        return bz2.BZ2File(filename, "rb")
    else:
        # open as normal file
        return codecs.open(filename, "r", "utf-8")


def get_linewise(
    filename, func=None, skip_comments="#", skip_empty_lines=True
):
    """
    read given file and return it linewise
    apply the given func on each line, if provided
    comments will be skipped
    """
    f = None
    try:
        # open file for reading
        f = open_read(filename)

        # prepare buffered reader for fast reading
        if hasattr(f, "read"):
            buffered_reader = io.BufferedReader(io.FileIO(f.fileno()))
        else:
            buffered_reader = io.BufferedReader(f)

        for line in buffered_reader:
            line = line.strip()

            if skip_empty_lines and (line == ""):
                # skip empty lines
                continue

            if (skip_comments is not None) and line.startswith(skip_comments):
                # skip comments
                continue

            yield func(line) if func is not None else line

    finally:
        # make sure file is closed
        if f is not None:
            f.close()


def get_lines_count(filename):
    """
    returns the number of lines in the file
    """
    return sum(1 for line in get_linewise(filename))


def get_all_files(pattern="*", directory=None, sort=True):
    """
    returns a list of all files in the given directory
    that matches the given pattern
    """
    if directory is not None:
        pattern = os.path.join(directory, pattern)

    files = glob.glob(pattern)

    if sort:
        files.sort()

    return files
