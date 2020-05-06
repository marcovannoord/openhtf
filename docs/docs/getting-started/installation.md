.. __installation_label_:
## Python Installation

[![PyPI version](https://badge.fury.io/py/spintop-openhtf.svg)](https://badge.fury.io/py/spintop-openhtf)


To install spintop-openhtf, you need Python. We officially support **Python 3.6+** for now. If you already have Python installed on your PC, you can skip this step. Officially supported OSes are:

- **Windows 10**
    
    Install Python using the Windows Installer: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

- **Raspbian & Ubuntu**

    Install through apt-get

### IDE: VS Code with Extensions

We use and recommend Visual Studio Code for the development of spintop-openhtf testbenches. Using it will allow you to:

- Seamlessly debug with breakpoints the code you will be writting
- Remotely develop on a Raspberry Pi if you wish to
- Use a modern, extendable and free IDE

#### Installation

1. [Download VS Code](https://code.visualstudio.com/download)
2. Run and follow the installation executable
3. Install the [Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

### Project Folder, Virtual Env & Installation (Windows)

First, create or select a folder where you want your sources to lie in.

Once you have your base python available, best practices are to create a virtualenv for each testbench you create. We will use `python` as the python executable, but if you installed a separate, non-path python 3 for example, you should replace that with your base executable.

Here are the installation steps on Windows:

1. Create Folder

    ```bat
    mkdir myproject
    cd myproject
    ```

2. Create venv

    ```bat
    # Creates new venv in the folder 'venv'
    python -m venv venv
    venv\Scripts\activate 
    ```

3. Install spintop-openhtf

    ```bat
    python -m pip install spintop-openhtf[server]
    ```
