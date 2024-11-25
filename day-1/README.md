# 2024 MLOps Summit Day 1

## Goals
* Environment Setup

## Initial Setup

### Proxy Setup

Run this command to configure your shell with access to download assets from the internet.
```
echo "export HTTP_PROXY="http://sysproxy.wal-mart.com:8080"
export HTTPS_PROXY=${HTTP_PROXY}
export https_proxy=${HTTP_PROXY}
export http_proxy=${HTTP_PROXY}
export NO_PROXY="*.samsclub.com,localhost,127.0.0.1,*.walmart.com,*.wal-mart.com" >> ~/.proxy.sh
source ~/.proxy.sh
```

Add the command `source ~/.proxy.sh` to your .bashrc or .zshrc file to ensure every shell has a properly configured proxy.


### Homebrew Setup

Homebrew is a free, open-source package manager that allows users to install, update, and manage software on macOS and Linux

To install homebrew, run the following command:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Python Setup

You can manage multiple python versions easily with a tool like anaconda or pyenv. In this section, we'll describe how to 
install both of these tools. We will also demonstrate how to install different python versions, switch between them, and set a default python version.

#### Conda

"Conda" in Python is an open-source package manager and environment management system that allows you to install, update, and manage various Python packages, including their dependencies, by creating isolated environments for different projects. A comprehensive list of conda commands can be found [here](https://docs.conda.io/projects/conda/en/stable/commands/index.html).

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

#### pyenv

pyenv is a simple python version management tool. It lets you easily switch between multiple versions of Python. It's simple, unobtrusive, and follows the UNIX tradition of single-purpose tools that do one thing well. A comprehensive list of pyenv commands can be found [here](https://github.com/pyenv/pyenv/blob/master/COMMANDS.md).

To install pyenv, run the following command:
```bash
brew install pyenv
```

Here are a few common commands for day to day usage:

```bash
#Install a specific version of python
pyenv install 2.7.6  

#List all installed versions of python
pyenv versions 

#Set the global version of python to be used in all shells
pyenv global 2.7.6

# Sets a local application-specific Python version by writing the version name to a .python-version file in the current directory. This version overrides the global version, and can be overridden itself by setting the PYENV_VERSION environment variable or with the pyenv shell command.
pyenv local 2.7.6 
```

### GCloud CLI

To install the gcloud cli and other google cloud sdk components, run the following command:

```bash
brew install --cask google-cloud-sdk
```

## IDE Setup

The following instructions will assume you're using Visual Studio Code (vscode), but the same can be achieved with PyCharm.

To install visual studio code, run the following command:

```bash
brew install --cask visual-studio-code
```

Once vscode is install, launch it and install the following extensions (View -> Extensions):

```
Python
Python Environment Manager
Python Debugger
Even Better TOML
Black Formatter
Pylance
GitLens -- Git supercharged
Docker
```