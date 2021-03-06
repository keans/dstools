import os
import sys
import gzip
import io
import glob
import codecs
import collections
import bz2
import shutil


# ----------- path ----------
def get_path_or_create(path):
    """
    returns the path and the flag, if it has been just created
    """
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.exists(path):
        os.makedirs(path)
        return path, True

    return path, False


def create_path_or_error(path):
    """
    create the path if not existing, else throw error
    """
    path = os.path.expanduser(path)
    if os.path.exists(path) and os.path.isdir(path):
        sys.exit("The path '%s' does already exist. Abort!" % path)

    # create the path
    os.makedirs(path)

    return path


def get_path_or_error(path):
    """
    returns the path or exists with an error, if it is not existing
    """
    path = os.path.expanduser(path)
    if not os.path.exists(path) or not os.path.isdir(path):
        sys.exit("The path '%s' does not exist. Abort!" % path)

    return path


def add_file_directory_to_path(f, rel_path=".."):
    """
    get the directory of the given path, joins it with the
    given rel_path and adds it to the path
    (normally just the __file__ of the calling module is provided)
    """

    path = os.path.abspath(
        os.path.join(os.path.expanduser(os.path.dirname(f)), rel_path)
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
def error_on_exists(filename):
    """
    raises error when file exists,
    returns given filename otherwise
    """
    if filename in (None, ""):
        sys.exit("No filename provided! Abort.")

    if os.path.exists(filename) and os.path.isfile(filename):
        sys.exit(
            "The filename '{}' does already exist! Abort.".format(filename)
        )

    return filename


def get_filename_or_error(filename, paths=[]):
    """
    tries to find the given filename in one of the paths in given order.
    If it exists the filename including the path will be returned,
    otherwise an error is raised
    """
    if filename in (None, ""):
        sys.exit("No filename provided! Abort.")

    # check direct match without path
    if os.path.exists(filename) and os.path.isfile(filename):
        return os.path.abspath(filename)

    if not isinstance(paths, list):
        paths = [paths]

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


def gzip_file(filename, keep=False):
    """
    reads the content of the given file linewise
    and stores it as gz file, by default the original
    file will be deleted, if keep flag is not set to true
    """
    with open(filename, "rb") as f_in, \
            gzip.open("{}.gz".format(filename), "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    if not keep:
        # remove original file, if flag is set
        os.remove(filename)


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
        # open as normal text file
        if (sys.version_info > (3, 0)):
            return open(filename, "rb")
        else:
            return codecs.open(filename, "r", "utf-8")


def get_blocks(filename, func=None, chunk_size=512):
    """
    read given file and return it blockwise
    (if None, all as one block is read)
    apply the given func on each block
    """
    with open_read(filename) as f:
        # prepare buffered reader for fast reading
        if not hasattr(f, "readable"):
            buffered_reader = io.BufferedReader(io.FileIO(f.fileno()))
        else:
            buffered_reader = io.BufferedReader(f)

        if chunk_size is None:
            # read complete file at once
            data = buffered_reader.read().decode("utf-8")
            yield func(data) if func is not None else data

        else:
            # read block wise
            while True:
                data = buffered_reader.read(chunk_size)
                if not data:
                    break
                yield func(data) if func is not None else data


def get_linewise(
    filename, func=None, skip_comments="#", skip_empty_lines=True
):
    """
    read given file and return it linewise
    apply the given func on each line, if provided
    comments will be skipped
    """
    with open_read(filename) as f:
        # prepare buffered reader for fast reading
        if not hasattr(f, "readable"):
            buffered_reader = io.BufferedReader(io.FileIO(f.fileno()))
        else:
            buffered_reader = io.BufferedReader(f)

        for line in buffered_reader:
            line = line.decode("utf-8").strip()

            if skip_empty_lines and (line == ""):
                # skip empty lines
                continue

            if (skip_comments is not None) and line.startswith(skip_comments):
                # skip comments
                continue

            try:
                yield func(line) if func is not None else line

            except ValueError as e:
                print("get_linewise ERROR: {} in '{}'".format(e, line))


def get_lines_count(filename):
    """
    returns the number of lines in the file
    """
    return sum(1 for line in get_linewise(filename))


def get_all_files(
    pattern="*", directory=None, sort=True, stop_on_empty=True
):
    """
    returns a list of all files in the given directory
    that matches the given pattern
    """
    if directory is not None:
        pattern = os.path.join(directory, pattern)

    files = glob.glob(os.path.expanduser(pattern))

    if sort:
        files.sort()

    if (stop_on_empty is True) and (len(files) == 0):
        sys.exit(
            "No files found for pattern '{}'! Abort.".format(pattern)
        )

    return files


def write_dict_to_file(d, filename, header=None):
    """
    write dictionary to file e.g. for storing used parameters
    """
    assert(isinstance(d, dict))

    with open(filename, "w") as f:
        if header is not None:
            # write header comment
            f.write("# {}\n".format(header))

        # write key, value pairs per line to text file
        f.writelines([
            "{} = {}\n".format(k, v)
            for k, v in d.items()
        ])
