# Automatic Speech Detection on a Smart Beehive‘s Raspberry Pi

This repository contains the code and tutorials for the detection of human speech in beehive audio data. It is part of our paper "Automatic Speech Detection on a Smart Beehive‘s Raspberry Pi", accepted for publication and presentation at LWDA2023 in Marburg, October 2023.

## Setup the system
If not already the case, upgrade the OS version of the Raspberry Pi to Bullseye.

Run `sudo apt-get -y update`.

Make sure that the dependencies _libatlas-base-dev_ and _libsndfile1_ are installed. (`sudo apt-get install`)

Check that the user, who executes the watcher script, is added to the group that can access the audio devices.

## Setup the environment
Clone the repository and navigate to it.

Run `pip install -r requirements.txt`.

## Setup system services needed for running the watcher script
Exemplary system service scripts for recording 60s audio files and converting them into FLAC-format are in the services_examples subfolder.

To mount a temporary filesystem, using tmpfs for example, run `sudo mkdir /mnt/ramdisk`.

Then open `/etc/fstab`and add the following entry at the bottom:  
`tmpfs /mnt/ramdisk tmpfs nodev,nosuid,size=100M 0 0`.

## Run the code

Our trained models, _bulbul_ (for embedding extraction) and a _k_-NN (for prediction on top) are in the models subfolder.

To evaluate the performance of a smart system -- a Raspberry Pi in our case --, run `python3 inference_evaluation.py --input-directory path/to/input/directory`.

This script classifies every .flac-file in the given directory and measures the duration of the successive steps during inference.

To deploy a watcher that processes every newly created .flac-file in a given directory of a temporary filesystem on the Raspberry Pi, run `python3 watcher.py --out-dir path/to/out/dir --dir-to-watch path/to/observed/dir`.

This script observes the directory, where the audio files recorded by the microphone of the Pi are stored on a temporary filesystem.
Upon the creation of a new .flac-file, the inference process is triggered and in case of a classification of the audio file as a sample which contains human speech, it is directly deleted from the temporary FS.
Individual procedures to process the non-human-speech samples after the inference can be added to the code.
