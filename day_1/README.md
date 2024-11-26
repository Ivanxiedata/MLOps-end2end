# 2024 MLOps Summit Day 1

## Goals
* Properly install/manage multiple python versions on a single workstation
* Setup your IDE to facilitate local development, testing, type hinting and inspection
* Learn how to create and test Kubeflow Pipelines

## Proxy Setup

Run this command to configure your shell with access to download assets from the internet.

```bash
# configure proxy variables in ~/.zshrc
echo "export HTTP_PROXY='http://sysproxy.wal-mart.com:8080'
export HTTPS_PROXY=${HTTP_PROXY}
export https_proxy=${HTTP_PROXY}
export http_proxy=${HTTP_PROXY}
export NO_PROXY='*.samsclub.com,localhost,127.0.0.1,*.walmart.com,*.wal-mart.com'" > ~/.proxy.sh

# reload shell with above shell profile changes
source ~/.proxy.sh
```

## Homebrew Setup

Homebrew is a free, open-source package manager that allows users to install, update, and manage software on macOS and Linux

To install homebrew, run the following command:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

[!NOTE]
This command may only work if you are off the walmart network.

## Git Setup

To install the git cli, run the following command:

```bash
brew install git
```

## Python Setup

You can manage multiple python versions easily with a tool like anaconda or pyenv. In this section, we'll describe how to 
install both of these tools. We will also demonstrate how to install different python versions, switch between them, and set a default python version.

### Conda

"Conda" in Python is an open-source package manager and environment management system that allows you to install, update, and manage various Python versions, including their dependencies, by creating isolated environments for different projects. A comprehensive list of conda commands can be found [here](https://docs.conda.io/projects/conda/en/stable/commands/index.html).

To install anaconda, run the following command:
```bash
brew install --cask anaconda
```

Here are a few common commands for day to day usage:

```bash
#Create a conda environment and specify a python version
conda create --name py3.10 python=3.10 

#List all installed versions of python
conda info --envs 

#Set the global version of python to be used in all shells
source activate py3.10

# export conda environment requirements list to a file
conda env export > environment.yml 
```

### pyenv

pyenv is a simple python version management tool. It lets you easily switch between multiple versions of Python. It's simple, unobtrusive, and follows the UNIX tradition of single-purpose tools that do one thing well. A comprehensive list of pyenv commands can be found [here](https://github.com/pyenv/pyenv/blob/master/COMMANDS.md).

To install pyenv, run the following command:
```bash
brew install pyenv
```

Here are a few common commands for day to day usage:

```bash
#Install a specific version of python
pyenv install 3.10

#List all installed versions of python
pyenv versions 

#Set the global version of python to be used in all shells
pyenv global 3.10

# Sets a local application-specific Python version by writing the version name to a .python-version file in the current directory. This version overrides the global version, and can be overridden itself by setting the PYENV_VERSION environment variable or with the pyenv shell command.
pyenv local 3.10 
```

### pip configuration

The following command configures pip to use the walmart artifactory pypi proxy:

```bash
mkdir -p ~/.pip && echo "[global]
index-url = https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/pythonhosted-pypi-release-remote/simple
trusted-host = repository.walmart.com" > ~/.pip/pip.conf
```
## GCloud CLI

To install the gcloud cli and other google cloud sdk components, run the following command:

```bash
brew install --cask google-cloud-sdk
```

A comprehensive set of commands can be found [here](https://cloud.google.com/sdk/docs/cheatsheet).


Run this command to authenticate to google cloud and configure the gcloud cli
```bash
gcloud auth application-default login
```

## IDE Setup

The following instructions will assume you're using Visual Studio Code (vscode), but the same can be achieved with PyCharm.

To install visual studio code, run the following command:

```bash
brew install --cask visual-studio-code
```

### Extensions
Launch VSCode and install the following extensions (View -> Extensions):
```
Python
Python Environment Manager
Python Debugger
Python Poetry
SonarLint
Even Better TOML
Black Formatter
Pylance
GitLens -- Git supercharged
Docker
Parquet Visualizer
Rainbow CSV
```

Next, we'll clone this repo

1. Hold Command+Shift+P to open the quick commands window. Type "Clone".
2. Select "Git: Clone"
3. Put this repo into the textbox: `https://gecgithub01.walmart.com/DataScienceServices/mlops-summit-2024.git` 
4. Hit Enter
5. Once cloning is complete, we'll next create a virtual environment. For the purposes of this demo, we will be using python 3.10.

 Create Virtual Environment
1. Hold Command+Shift+P to open the quick commands window. Type "Create Environment".
2. Select "Python: Create Environment".
3. Select "Venv".
4. Depending on whether you're using conda or v, you will see various options. Choose a version of python compatibile with 3.10.
5. Open a Terminal (Terminal -> New Terminal or Ctrl+`)
6. Ensure you see (.venv) at the beginning of the prompt. This lets you know that your shell is bound to our new virtual environment
7. Run `pip install poetry`
8. After poetry is installed, run `poetry install` to install dependencies in your virtual environment, and install the day_* 
modules in editable mode.

Allow the dependencies from the pyproject.toml file to install. Once complete, open [hello_world_pipeline.py](./hello_world_pipeline.py). Ensure you do not see 
red/yellow squigglies underlining imports or other code in the file.

Next, we'll go over:
1. Code navigation in the IDE
2. Dependency management with pip vs poetry
3. Running unit tests
4. How to use vscode's git integration to perform branch management
5. Kubeflow Pipeline, Components, and Input/Output Overview
6. Run a Hello World Kubeflow Pipeline and observe the outputs