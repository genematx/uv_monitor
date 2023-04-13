# uv_monitor

An example repository exploring the UV-B monitoring dataset from the [National Resource Ecology Laboratory](https://www.nrel.colostate.edu/) at CSU.


## Getting Started

The dataset can be downloaded from the oficial NREL [website](https://uvb.nrel.colostate.edu/UVB/data-sets-download/). In this example, we use the Erythemal weighted irradiance data for locations in Colorado and New Zealand; the required csv files can be downloaded and prepared with a convenience script by running `make unzip-data` in the terminal.

The code is written in tested in Python 3.11. The required packages are managed with [poetry](https://python-poetry.org/), and the software is conteinerized with [Docker](https://www.docker.com/).

The database querying functionality uses the OpenAI GPT model and requires an API key to be set up; the key can be obtained [here](https://openai.com/blog/openai-api).


## Repository Contents

* `src/uv_monitor` - main .py files:
    * dataio.py - utilities for loading and saving the data;
    * logging.py - defines and configures a project-wide logger;
    * anomaly.py - time-series anomaly detection for data quality assesment;
    * utils.py - other helper functions, e.g. for plotting.

* `notebooks` - Jupyter notebooks useful for data exploration. To reduce the amount of data stored in the remote repository, the notebooks can be converted from `.ipynb` format to `.py` files with the jupytext utility. For this run the following command in the terminal:

    ```
    poetry run jupytext --set-formats ipynb,py notebooks/*
    ```

* `tests` - unit tests implemented with pytest. Run `make test` to perform the testing.

* `app` - an example of a web-interface for the data query app. The following command will initialize the app, start a local web server, and open the browser:

    ```
    poetry run python app/app.py
    ```

    Alternatively, one can deploy the app in the Docker container by calling `make run-app` and then navigate to <http://localhost:7860> in the browser.

* `docker` - definitions of the Docker image.

* `.github/workflows` - definitions of the CI/CD pipeline on GitHub that performs testing, formatting, and linting of the code on each push to the remote repository. These actions can be done locally as well by running `make test`, `make fmt`, and `make lint` respectively.
