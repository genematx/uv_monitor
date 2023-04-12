from typing import Union

import pandas as pd
from prophet import Prophet

from .logging import logger


class DailyAnomalyDetector:
    """Anomaly detector in one-dimensional timeseries with daily periodicity.

    Attributes:
        model (Prophet or other): A Prophet or another ML model used to detect anomalies
        conf_interval (float): The confidence (credible) interval for the predictions.
        clip_negative (bool): Whether to clip predicted negative values to zero.
    """

    def __init__(self, model: str = "prophet", conf_interval: float = 0.95, clip_negative=True):
        # TODO: add other models
        if model == "prophet":
            self._model = Prophet(
                interval_width=conf_interval,
                yearly_seasonality=True,
                weekly_seasonality=False,
            )
        self.clip_negative = clip_negative

    def __prepare_data_for_prophet(self, data: pd.Series) -> pd.DataFrame:
        """Prepare the data for anomaly detection with Prophet.

        Args:
            data (pd.Series): A DataSeries containing the data to detect anomalies in;
            the index should be datetime-compatible.

        Returns:
            A pandas DataFrame containing columns named 'ds' and 'y'.
        """

        # Prophet requires columns named 'ds' for datetime index and 'y' for the data
        data.index.rename("ds", inplace=True)
        data = data.rename("y").sort_index().reset_index()
        data["ds"] = pd.to_datetime(data["ds"])

        return data

    def fit(self, data: pd.Series):
        """Fit the model to the data.

        Args:
            data (pd.Series): A DataSeries containing the training data to fit the model
                to; the index should be datetime-compatible.
        """

        logger.info(f"Fitting model to data; dataset size = {data.shape[0]}")
        data = self.__prepare_data_for_prophet(data)
        self._model.fit(data)

        return self

    def predict(self, data: pd.Series):
        """Predict anomalies in the data.

        Args:
            data (pd.Series): A DataSeries containing the training data to fit the model
                to; the index should be datetime-compatible.
        """

        logger.info(f"Predicting anomalies in data; dataset size = {data.shape[0]}")
        data = self.__prepare_data_for_prophet(data)
        preds = self._model.predict(data)

        # Keep only the relevant columns
        preds = preds[["ds", "yhat", "yhat_lower", "yhat_upper"]]

        # Threshold predicted negative values to zero
        if self.clip_negative:
            preds["yhat"] = preds["yhat"].clip(lower=0)
            preds["yhat_lower"] = preds["yhat_lower"].clip(lower=0)
            preds["yhat_upper"] = preds["yhat_upper"].clip(lower=0)

        # Merge the predictions with the original data
        preds = data.merge(preds, on="ds", how="left").set_index("ds")

        # Detect anomalies
        preds["is_anomaly"] = (preds["y"] > preds["yhat_upper"]) | (
            preds["y"] < preds["yhat_lower"]
        )

        return preds
