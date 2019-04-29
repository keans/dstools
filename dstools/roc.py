import logging

import ujson as json
import numpy as np
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
from matplotlib import ticker

from .plot import FigureContext

# disable extensive matplotlib logging
logging.getLogger("matplotlib").setLevel(logging.WARNING)

# logger
log = logging.getLogger(__name__)


class RocCurve:
    """
    class that abstracts some of the logic of the
    Receiver Operating Characteristics (ROC) curve
    """
    def __init__(self, labels=None, scores=None, name="ROC"):
        self._name = name

        if (labels is not None) and (scores is not None):
            # compute roc curve, if provided
            assert(len(labels) == len(scores))
            self.compute_roc_curve(labels, scores)

    def compute_roc_curve(self, labels, scores):
        """
        compute the ROC curve for given labels and scores
        """
        self._fpr, self._tpr, self._thresholds = roc_curve(labels, scores)

    @property
    def dict(self):
        return {
            "name": self._name,
            "fpr": self._fpr,
            "tpr": self._tpr,
        }

    def auc(self, max_fpr=1.0):
        """
        compute (bounded-)AUC for ROC curve
        """
        return self._bounded_auc(self._fpr, self._tpr, max_fpr)

    def _bounded_auc(self, fpr, tpr, max_fpr=None):
        """
        compute the bounded AUC of a ROC curve on given
        false positive rate and true positive rate
        """
        if (max_fpr is None) or (max_fpr == 1.0):
            # just return full auc i.e. without modifications
            return fpr, tpr, auc(fpr, tpr)

        # compute bounded auc
        stop = np.searchsorted(fpr, max_fpr, "right")
        x_interp = [fpr[stop - 1], fpr[stop]]
        y_interp = [tpr[stop - 1], tpr[stop]]
        tpr = np.append(tpr[:stop], np.interp(max_fpr, x_interp, y_interp))
        fpr = np.append(fpr[:stop], max_fpr)

        # McClish correction: standardize result to be 0.5,
        # if non-discriminant and 1 if maximal
        min_area = 0.5 * max_fpr ** 2
        auc_ = 0.5 * (1 + (auc(fpr, tpr) - min_area) / (max_fpr - min_area))

        return fpr, tpr, auc_

    def plot(self, ax, max_fpr=1.0, title=None, random_line=True):
        # prepare label
        label = "{} ({}AUC={:0.3f})".format(
                self._name,
                (
                    "{}-bounded, ".format(max_fpr)
                    if max_fpr not in (None, 1.0)
                    else ""
                ),
                self.auc(max_fpr)[2]
        )

        # plot ROC curve
        ax.plot(self._fpr, self._tpr, label=label)

        # plot random predictions line
        if random_line is True:
            plt.plot([0, 1], [0, 1], "k--")

        ax.xaxis.set_major_locator(ticker.MaxNLocator(prune='lower'))
        plt.xlim([0.0, max_fpr or 1.0])
        plt.ylim([0.0, 1.0])

        if title is not None:
            plt.title(title)

        plt.legend(loc="best")

    def save(self, filename):
        """
        save given ROC curve as .json file
        """
        log.debug("saving ROC curve to '{}'...".format(filename))
        with open(filename, "w") as f:
            json.dump(self.dict, f)

    def load(self, filename):
        """
        save given ROC curve as .json file
        """
        log.debug("loading ROC curve from '{}'...".format(filename))
        with open(filename, "r") as f:
            d = json.load(f)
            self._fpr = d["fpr"]
            self._tpr = d["tpr"]
            self._name = d["name"]


def plot_rocs(
    rocs, targetdir, filename="roc", max_fpr=None, random_line=True,
    title=None, figsize=(10, 8), ext="pdf"
):
    """
    plot multiple ROC curves into one figure
    list of rocs must contain dictionaries with the following keys:
        "fpr", "tpr", "auc_score", "label"
    """
    if isinstance(rocs, RocCurve):
        # convert single roc dict into list
        rocs = [rocs]

    with FigureContext(
        targetdir=targetdir, filename=filename, title=title,
        xlabel="False Positive Rate", ylabel="True Positive Rate",
        rotate_xticks=False, ext=ext
    ) as ax:
        for roc in rocs:
            roc.plot(ax, max_fpr, title, random_line)

        return plt.gcf()
