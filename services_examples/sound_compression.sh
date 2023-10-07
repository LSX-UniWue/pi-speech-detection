#!/usr/bin/env bash

COMPRESSION_LEVEL=3
DESTINATION="/tmp/we4bee/audio"  # location in the temporary filesystem, where the final .flac file is saved to

INPUT_FILE="$1"
OUTPUT_FILE="$2"
CHANNELS="$3"

flac --compression-level-${COMPRESSION_LEVEL} --silent -o ${DESTINATION}/${OUTPUT_FILE}.flac ${INPUT_FILE}
rm ${INPUT_FILE}
