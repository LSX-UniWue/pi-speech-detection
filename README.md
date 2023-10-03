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

Make sure that the user, who executes the inference scripts, is added to the group that can access the audio devices.

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

## Run the code

Our trained models, _bulbul_ (for embedding extraction) and a _k_-NN (for prediction on top) are in the models subfolder.

To evaluate the performance of a smart system -- a Raspberry Pi in our case --, run `python3 inference_evaluation.py --input-directory path/to/input/directory`.

This script classifies every .flac-file in the given directory and measures the duration of the successive steps during inference.

To deploy a watcher that processes every newly created .flac-file in a given directory of a temporary filesystem on the Raspberry Pi, run `python3 watcher.py --out-dir path/to/out/dir --dir-to-watch path/to/observed/dir`.

This script observes the directory, where the audio files recorded by the microphone of the Pi are stored on a temporary filesystem.
Upon the creation of a new .flac-file, the inference process is triggered and in case of a classification of the audio file as a sample which contains human speech, it is directly deleted from the temporary FS.
Individual procedures to process the non-human-speech samples after the inference can be added to the code.
