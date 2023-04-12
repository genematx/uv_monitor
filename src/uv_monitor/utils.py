from typing import Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd


def plot_anomaly(
    preds: pd.DataFrame,
    ax: plt.Axes,
    date_range: Optional[Tuple[str, str]] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = "Date",
    ylabel: Optional[str] = None,
):
    """Plot the detected anomalies in the data.

    Args:
        preds (pd.DataFrame): A DataFrame containing the predictions from the model as
            returned by the `predict()` method of the `DailyAnomalyDetector` class.
        ax (plt.Axes): The axes to plot the data on.
        date_range (pair of str, optional): A tuple containing the start and end dates
            in the format 'YYYY-MM-DD' to plot. Defaults to None (plot all data).
        title (str, optional): The title of the plot.
        xlabel (str, optional): The label of the x-axis.
        ylabel (str, optional): The label of the y-axis.
    """

    ax.fill_between(
        preds.index, preds["yhat_lower"], preds["yhat_upper"], color="b", alpha=0.2
    )
    preds.plot(y="yhat", use_index=True, ax=ax, linewidth=1, color="b")
    ax.scatter(
        preds.index,
        preds["y"],
        s=[3 if flag else 1.5 for flag in preds["is_anomaly"]],
        c=["r" if flag else "b" for flag in preds["is_anomaly"]],
    )
    ax.get_legend().remove()
    ax.autoscale(enable=True, axis="x", tight=True)
    if date_range is not None:
        ax.set_xlim([pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])])
    if title is not None:
        ax.set_title(title)
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
