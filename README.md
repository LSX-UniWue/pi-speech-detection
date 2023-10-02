# Automatic Speech Detection on a Smart Beehive‘s Raspberry Pi

This repository contains the code and tutorials for the detection of human speech in beehive audio data. It is part of our paper "Automatic Speech Detection on a Smart Beehive‘s Raspberry Pi", accepted for publication and presentation at LWDA2023 in Marburg, October 2023.

## Setup the system
Run:

```
sudo apt update
sudo apt upgrade
```

(In case "sudo apt update" doesn't work: change the url part of the first entry in "/etc/apt/sources.list" to "http://legacy.raspbian.org/raspbian/")

If necessary, run:

```
sudo apt-get install cmake
```

Upgrade the python version to 3.9.2, if necessary.

## Setup the environment
Clone the repository and navigate to it.

Run the following commands:

```bash
python -m venv your_venv_name

source your_venv_name/bin/activate

pip install -r requirements.txt
```

In case "pip install" doesn't work because of an "pip is configured with locations that require TLS/SSL, however the ssl module in Python is not available" error, try this:

```bash
sudo apt install libssl-dev libncurses5-dev libsqlite3-dev libreadline-dev libtk8.6 libgdm-dev libdb4o-cil-dev libpcap-dev libffi-dev libatlas-base-dev
```

then cd to the folder with the Python 3.X library source code and run:

```bash
./configure 
sudo make 
sudo make install
```
## Setup system services

## Run the code
