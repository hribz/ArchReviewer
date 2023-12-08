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
    sudo apt-get install python2-dev libxml2-dev libxslt-dev zlib1g-dev python-setuptools
    ```

    install srcml from https://www.srcml.org/#download
    ```bash
    wget http://131.123.42.38/lmcrs/v1.0.0/srcml_1.0.0-1_ubuntu20.04.deb
    sudo dpkg -i srcml_1.0.0-1_ubuntu20.04.deb
    ```

    if install srcml failed and hint 'Package libssl1.1 is not available'

    ```bash
    wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1-1ubuntu2.1~18.04.23_amd64.deb
    sudo dpkg -i libssl1.1_1.1.1-1ubuntu2.1~18.04.23_amd64.deb
    ```

3. install Python package

    ```bash
    sudo python setup.py install
    ```

4. supply work folder path in 'input.txt', for example:

    ```
    /path/to/ArchReviewer/test
    ```
    
    and the source code to analysis should be stored at path '/path/to/ArchReviewer/test/source'

5. run command

    ```bash
    ArchReviewer --kind=archinfo
    ```

    then, analysis result will be store at path '/path/to/ArchReviewer/test/_ArchReviewer'