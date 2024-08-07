# Conda

1. Create a virtual environment
   * `conda create --name my_env_name python=3.8` or whatever Python version you may need.
2. List available envs (2 different ways
   * `conda env list`
   * `conda info --envs`
3. Activate virtual env
   * `conda activate my_env_name`
4. Deactivate current environment
   * `conda deactivate`
5. If pip doesn't work with a fresh conda install:
   * `conda install pip`
6. Install project dependencies (listed in requirements.txt file)
   * `conda install --file requirements.txt`
   * `pip install -r requirements.txt`
7. Delete an old environment
   * `conda remove --name my_env_name --all`
   * `conda env remove -n my_env_name`
8. Update conda
   * `conda update conda`
9. Update all packages in the current environment
   * `conda update --all`
10. Update all packages in another env
    * `conda update -n my_env_name --all`
11. List installed packages in current environment
    * `conda list`
12. Add conda-forge channel
    * `conda config --add channels conda-forge`
13. Check conda channels
    * `conda config --show channels`
14. Remove conda-forge channel
    * `conda config --remove channels conda-forge`
15. Create an environment file from your current environment.
    * `conda env export --from-history > environment.yml`
16. Create a new environment and install dependencies listed in YML file.
    * `conda env create -f environment.yml`
17. If you don't want the base environment to load automatically whenever you open a new shell, change the configs:
    * `conda config --set auto_activate_base false`

# Pipenv + Pyenv

`pyenv` is a Python version manager. It allows you to install and manage multiple Python versions.

`pipenv` is a Python virtualenv management tools. `pipenv` does not have built-in package search; make sure you search for the packages at [PyPI](https://pypi.org/).

### Installation

1. `pyenv`
    * https://github.com/pyenv/pyenv
    * `pyenv` can be installed with either Brew or with the automatic installer script.
    * For Windows, there is `pyenv-win` but I have not tested it.
    * For Ubuntu 22.04 LTS, make sure you run the following before installing:
        * `sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm xz-utils tk-dev libffi-dev liblzma-dev python3-openssl`
1. `pipenv`
    * https://pipenv.pypa.io/en/latest/index.html
    * Install locally for your user with `pip install pipenv --user`

### Usage

The environments are based on the folder you're on. There is no need to manually name them, and there is no environment activation to take care of per se.

1. Install the Python version you need
    * `pyenv install 3.11`
1. Create a new virtual environment with pipenv and choose the Python vrsion you want.
    * `pipenv install --python 3.11`
3. Install a package (this will modify `Pipfile` and `Pipfile.lock`)
    * `pipenv install some_package`
    * `pipenv install some_package=1.0`
4. If a `Pipfile.lock` file already exists, you can install the packages from it.
    * `pipenv sync`
5. Update packages
    * `pipenv update` > updates all packages
    * `pipenv update <package>` updates a single package and its sub-dependencies
6. Access the pipenv shell (necessary for enabling the virtualenv and for your script to find the installed packages).
   * `pipenv shell`
7. Exit a pipenv shell.
   * `exit`
8. Install all dependencies to the system, avoiding virtualenvs entirely (useful for deployment in containers)
   * `pipenv install --system --deploy` > Use this in your Dockerfile.

# Installing pipenv on Docker Dev Environment

* Update apt

      sudo apt update && sudo apt upgrade
* Install pip

      sudo apt install python3-pip
* Install pyenv. Follow instructions here: https://github.com/pyenv/pyenv-installer
* Install pipenv. Follow instructions here: https://pipenv.pypa.io/en/latest/