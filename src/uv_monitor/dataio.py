import pandas as pd
from io import StringIO
from typing import Union

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
        if line.startswith('#Location:'):
            result['loc_name'] = line.split(':')[1].strip()
        elif line.startswith('#Latitude:'):
            val, dir = line.split(':')[1].split()
            result['lat'] = float(val) if dir == 'N' else -float(val)
        elif line.startswith('#Longitude:'):
            val, dir = line.split(':')[1].split()
            result['lon'] = float(val) if dir == 'E' else -float(val)
        elif line.startswith('#Elevation:'):
            result['elev'] = float(line.split(':')[1].split()[0].strip())
        elif line.startswith('#Internal ID:'):
            result['loc_id'] = line.split(':')[1].strip()

    return result


def read_csv_file(filepath: str, num_header_rows:int = 18) -> Union[pd.DataFrame, str]:
    """Read a CSV file into a pandas dataframe and return the header rows as a string.
    
    Args:
        filepath (str): The path to the CSV file.
        num_header_rows (int): The number of header rows to read into the string buffer.

    Returns:
        A dataframe containing the data from the CSV file and a string containing the
        header rows.
    """

    with open(filepath, 'r') as f:
        # read header rows into string buffer
        header = ''
        for i in range(num_header_rows):
            header += f.readline()

        # read data part of CSV file into dataframe
        df = pd.read_csv(StringIO(f.read()))

    return df, header