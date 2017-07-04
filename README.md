# nhs-choices-pharmacies
Some simple code to download a subset of pharmacy data from the NHS Choices Syndication API

## Getting Started
This is a Python 3 project - you will need Python 3 and Pip installed on your machine before you get started.

You can use either Pipenv or Virtualenv and Pip to manage your environment.
Both Pipenv and requirements.txt dependency files are provided.

### Setting up an environment using Pipenv

For more information on Pipenv have a look here: [Pipenv on Github](https://github.com/kennethreitz/pipenv/blob/master/README.rst)

You can install Pipenv using Pip:

`$ pip install pipenv`

Create an Python 3 environment:

`$ pipenv --three`

Then install the package dependencies:

`$ pipenv install`

Pipenv will set you up a new virtual environment and install the packages for you.

Then activate the environment shell so that you can run the code:

`$ pipenv shell`


### Running the Code

Before you run the code, you will need to set a couple of configuration settings.

Define your API Key either by setting an environment variable called 'API_KEY' or 
by updating the default value in `pharmacy.py`.

You can also define the results page number that you want to start the download from.
There are currently 385 pages of pharmacy results so if you want to run a quick test, 
start from page 380 for example.

Once you're ready to run the download code, do the following:

`$ python pharmacy.py`

