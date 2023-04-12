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

# # Demo of the Data Query with LangChain

# +
# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

import matplotlib.pyplot as plt
import pandas as pd
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain

from dotenv import load_dotenv
load_dotenv()

# +
# create a connection to the SQLite database
conn = sqlite3.connect('../data/uvb.db')

# query the database using SQL
query = "SELECT * \
        FROM erythemal INNER JOIN locations \
        ON erythemal.loc_id = locations.loc_id \
        WHERE erythemal.loc_id IN ('CO11', 'NZ01') \
        ORDER BY RANDOM() \
        LIMIT 5"

# print the result
result = pd.read_sql_query(query, conn)
print(result)

# close the database connection
conn.close()
# -

db = SQLDatabase.from_uri("sqlite:///../data/uvb.db")
llm = OpenAI(temperature=0)
db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)
# db_chain.run("Which location has seen the highest total erythemal irradiance in March 2022?")
db_chain.run("Across all locations in Colorado, what was the sunniest day in March 2022?")



