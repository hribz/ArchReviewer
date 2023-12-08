# ArchReviewer

## Overview

System:

* Linux/Ubuntu
* Python 2.x (Python3 is not support)
* srcML 1.0.0

## Configure & Build

1. get source code

    ```bash
    git clone https://github.com/hribz/ArchReviewer.git
    ```

2. install neccessary libarary

    ```bash
    sudo apt-get install astyle
    sudo apt-get install xsltproc
    sudo apt-get install libxml2 libxml2-dev
    sudo apt-get install gcc
    sudo apt-get install python-dev libxml2-dev libxslt-dev zlib1g-dev
    sudo apt-get install srcml
    ```

3. install Python package

    ```bash
    sudo python setup.py install
    ```
