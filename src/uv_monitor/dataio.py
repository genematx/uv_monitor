import os
from io import StringIO
from typing import Union

import pandas as pd

from .logging import logger


def parse_header(header: str) -> dict:
    """Parse the header of an erythemal weighted irradiance data file into a dictionary.

    The latitude and longitude are converted to decimal degrees with negative values for
    the southern and western hemispheres respectively. The elevation is expressed in
    meters.

    Args:
        header (str): The header of an erythemal weighted irradiance data file.

    Returns:
        dict: A dictionary containing the location name and id, latitude, longitude, and
        elevation.
    """

    result = {}
    for line in header.splitlines():
        if line.startswith("#Location:"):
            result["loc_name"] = line.split(":")[1].strip()
        elif line.startswith("#Latitude:"):
            val, dir = line.split(":")[1].split()
            result["lat"] = float(val) if dir == "N" else -float(val)
        elif line.startswith("#Longitude:"):
            val, dir = line.split(":")[1].split()
            result["lon"] = float(val) if dir == "E" else -float(val)
        elif line.startswith("#Elevation:"):
            result["elev"] = float(line.split(":")[1].split()[0].strip())
        elif line.startswith("#Internal ID:"):
            result["loc_id"] = line.split(":")[1].strip()

    return result


def read_csv_file(filepath: str) -> Union[pd.DataFrame, str]:
    """Read a CSV file into a pandas dataframe and return the header rows as a string.

    The topmost rows starting with # are considered to be the header.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        A dataframe containing the data from the CSV file and a string containing the
        header rows.
    """

    with open(filepath, "r") as f:
        # read header rows into string buffer
        header = ""
        for line in f:
            if line.startswith("#"):
                header += line
            else:
                # parse and clean column names from first line of data
                cols = [c.strip() for c in line.split(",")]
                break

        # read data part of CSV file into dataframe (incl. the last line read in loop)
        df = pd.read_csv(StringIO(f.read()), low_memory=False, names=cols)

    return df, header


def read_folder(dirpath: str) -> Union[pd.DataFrame, pd.DataFrame]:
    """Read all CSV files in a folder and merge the data into a single dataframe.

    The header rows of each file are parsed and used to create a dataframe of locations.

    Args:
        dirpath (str): The path to the folder containing the CSV files.

    Returns:
        Two dataframes: one containing the merged data from all CSV files and one with
        the locations attributes.
    """

    # filter only csv files
    all_files = [file for file in os.listdir(dirpath) if file.endswith(".csv")]
    logger.info(f"Found {len(all_files)} CSV files in {dirpath}")

    dfs, headers = [], []
    for file in all_files:
        logger.info(f"Reading data from {file}")
        df, header = read_csv_file(os.path.join(dirpath, file))
        dfs.append(df)
        headers.append(header)

    # merge all dataframes into one
    merged_df = pd.concat(dfs, ignore_index=True)

    # Create a dataframe of unique locations
    df_loc = pd.DataFrame([parse_header(h) for h in headers]).drop_duplicates("loc_id")

    return merged_df, df_loc
