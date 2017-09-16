import os
import sys
import gzip
import io
import glob
import codecs
import collections

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

    if paths == []:
        # if no path provided, use current directory
        paths = ["./"]

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


def get_linewise(filename, linewise_json=False):
    """
    read given file and return it linewise
    """
    f = None
    try:
        if filename.endswith(".gz"):
            # open as gzip
            f = gzip.open(filename, "rb")
            buffered_reader = io.BufferedReader(f)
        else:
            # open as normal file
            f = codecs.open(filename, "r", "utf-8")
            buffered_reader = io.BufferedReader(io.FileIO(f.fileno()))

        for line in buffered_reader:
            if line.startswith("#"):
                # skip comments
                continue

            if linewise_json:
                # decode linewise json
                yield json.loads(line)

            else:
                # return stripped vanilla line
                yield line.strip()

    finally:
        # make sure file is closed
        f.close()


def get_lines_count(filename):
    """
    returns the number of lines in the file
    """
    return sum(1 for line in get_linewise(filename))


def get_all_files(directory, pattern="*", sort=True):
    """
    returns a list of all files in the given directory
    that matches the given pattern
    """
    files = glob.glob(os.path.join(directory, pattern))

    if sort:
        files.sort()

    return files
