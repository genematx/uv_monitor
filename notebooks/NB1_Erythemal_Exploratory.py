# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Exploratory Notebook for the Erythemal Irradiance Data
# Load the dataset and find average daily irradinace across different locations. Use anomaly detection to find potentially erroneous data entries.

# +
# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

import matplotlib.pyplot as plt
import pandas as pd
from prophet import Prophet
import sqlite3

import numpy as np
import seaborn as sns

# -

from uv_monitor.logging import logger
from uv_monitor.dataio import parse_header, read_csv_file, read_folder
from uv_monitor.anomaly import DailyAnomalyDetector
from uv_monitor.utils import plot_anomaly

df, header = read_csv_file("../data/Ontario-Toronto-2022-ery.csv")
print(header)
df.head(5)

df, df_loc = read_folder("../data")

# +
# Extract the date and time columns; find the total number of seconds since midnight
df["date"] = pd.to_datetime(df["Local Date"], format="mixed").dt.date
df["time"] = pd.to_datetime(df["Local Date"], format="mixed").dt.time
df["time_sec"] = df["time"].apply(lambda x: x.hour * 3600 + x.minute * 60 + x.second)
df = df.sort_values(["date", "time_sec"])

# Update column names
df = df.drop(columns=["UTC Date", "Local Date", "Local DOY"])
df.columns = [col.lower() for col in df.columns]
df.rename(columns={"id": "loc_id"}, inplace=True)

# +
# Find the sampling period for each record
df["time_diff_sec"] = (
    df.groupby(["loc_id", "date"])["time_sec"].diff().fillna(method="backfill")
)

# Find the integrated erythemal irradiance, W/m2*sec
df["intgr_erythemal"] = df["erythemal"] * df["time_diff_sec"]
# -

df.sample(10)

df_loc.sample(10)

# +
# Save the processed data in a local SQLite DB
conn = sqlite3.connect("../data/uvb.db")

# write the data frames to the database
df.to_sql(name="erythemal", con=conn, if_exists="replace", index=False)
df_loc.to_sql(name="locations", con=conn, if_exists="replace", index=False)

# close the database connection
conn.close()

# +
# Find average daily erythemal irradiance
df_daily = df.groupby(["loc_id", "date"])[["intgr_erythemal", "time_diff_sec"]].sum()
df_daily = df_daily["intgr_erythemal"] / df_daily["time_diff_sec"]
df_daily = df_daily.rename("avg_erythemal").reset_index()

df_daily.sample(5)

# +
fig, ax = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
df_daily[df_daily["loc_id"] == "CO11"].plot(x="date", y="avg_erythemal", ax=ax[0])
df_daily[df_daily["loc_id"] == "NZ01"].plot(x="date", y="avg_erythemal", ax=ax[1])

ax[0].set_title("Steamboat Springs, CO")
ax[1].set_title("Alexandra, NZ")

ax[0].set_ylabel("Avg erythemal irradiance, $W/m^2$")
ax[1].set_ylabel("Avg erythemal irradiance, $W/m^2$")

# +
ser_co = (
    df_daily.loc[df_daily["loc_id"] == "CO11", ["date", "avg_erythemal"]]
    .set_index("date")
    .squeeze()
)
ser_nz = (
    df_daily.loc[df_daily["loc_id"] == "NZ01", ["date", "avg_erythemal"]]
    .set_index("date")
    .squeeze()
)

# ser_co.plot()
# -

data_CO = (
    df_daily.loc[df_daily["loc_id"] == "CO11", ["date", "avg_erythemal"]]
    .set_index("date")
    .squeeze()
)
data_NZ = (
    df_daily.loc[df_daily["loc_id"] == "NZ01", ["date", "avg_erythemal"]]
    .set_index("date")
    .squeeze()
)

# +
model_CO = DailyAnomalyDetector().fit(data_CO)
preds_CO = model_CO.predict(data_CO)

model_NZ = DailyAnomalyDetector().fit(data_NZ)
preds_NZ = model_NZ.predict(data_NZ)
# -

preds_CO.sample(10)

# +
sns.set()

fig, ax = plt.subplots(2, 1, figsize=(15, 10), sharex=True)

plot_anomaly(
    preds_CO,
    ax[0],
    ("2016-01-01", "2022-07-01"),
    title="Steamboat Springs, CO",
    ylabel="Avg Erythemal Irradiance, $W/m^2$",
)
plot_anomaly(
    preds_NZ,
    ax[1],
    ("2016-01-01", "2022-07-01"),
    title="Alexandra, NZ",
    ylabel="Avg Erythemal Irradiance, $W/m^2$",
)

plt.show()
