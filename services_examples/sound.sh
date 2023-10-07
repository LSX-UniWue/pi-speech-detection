#!/usr/bin/env bash

SAMPLE_RATE=44100
DESTINATION="/tmp/we4bee/wavs"  # location in the temporary filesystem, where the recorded .wav files are saved to
LOCATION="${HOME}/code-we4bee-sensor_network/scripts/sound_compression.sh"  # location of the sound compression script
DEVICE="plughw:Device"  # ID of the used microphone
CHUNK_SIZE_IN_S=60  # 1 minute
QUALITY="cd"
CHANNELS=2

while :
do
    ts=$( date +%Y-%m-%dT%H:%M:%S%z )
    file="${DESTINATION}/${ts}"
    arecord -D ${DEVICE} -f ${QUALITY} -t wav -c ${CHANNELS} -r ${SAMPLE_RATE} -d ${CHUNK_SIZE_IN_S} --use-strftime ${file}.wav
    bash ${LOCATION} ${file}.wav ${ts} ${CHANNELS} &
done
