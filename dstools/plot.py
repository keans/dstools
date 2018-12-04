import os
import logging

import matplotlib
import matplotlib.pyplot as plt


# disable extensive matplotlib logging
logging.getLogger("matplotlib").setLevel(logging.WARNING)

# logger
log = logging.getLogger(__name__)


class FigureContext:
    """
    context manager that abstracts the creation of the figure
    and storing the final result in a file
    """
    def __init__(
        self, targetdir, title, xlabel="x", ylabel="y", rotate_xticks=True,
        figsize=(15, 10), dpi=300, tight_layout=True, ext="pdf"
    ):
        self._targetdir = targetdir
        self._title = title
        self._figsize = figsize
        self._dpi = dpi
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._rotate_xticks = rotate_xticks
        self._tight_layout = tight_layout
        self._ext = ext

    def __enter__(self):
        fig, ax = plt.subplots(figsize=self._figsize)

        plt.xlabel(self._xlabel)
        plt.ylabel(self._ylabel)

        if self._rotate_xticks is True:
            plt.xticks(rotation=90)

        matplotlib.rc("xtick", labelsize=8)
        matplotlib.rc("ytick", labelsize=8)

        return ax

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self._tight_layout is True:
            plt.tight_layout()

        output_filename = os.path.join(
            self._targetdir, "{}.{}".format(self._title, self._ext)
        )
        log.debug("writing graph to '{}'...".format(output_filename))
        plt.savefig(output_filename, bbox_inches="tight", dpi=self._dpi)
        plt.close()
