import csv
import glob
import os
import time

import sklearn.neighbors
import tflite_runtime.interpreter as tflite
import soundfile
from scipy.signal import resample
import argparse
import pickle
import numpy as np
from datetime import datetime
from sklearn.metrics import classification_report


def create_confusion_matrix(labels, predictions):
    cm = sklearn.metrics.confusion_matrix(labels, predictions)
    return cm


def get_class_of_file(filepath: str) -> int:
    if "nonhuman" in filepath:
        return 0
    else:
        return 1


def logs_to_csv(logs):
    with open('logs.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['file', 'label', 'predicted'])
        for log in logs:
            writer.writerow(log)


def reshape_input_data(data):
    data = np.expand_dims(data, axis=0)
    return np.expand_dims(data, axis=-1)


def load_knn(path_to_knn: str):
    with open(path_to_knn, 'rb') as f:
        knn = pickle.load(f)
    return knn


def main(args):
    start = time.time()
    interpreter = tflite.Interpreter(model_path=args.model_file)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print("Loading TFlite model took: ", time.time() - start)

    start = time.time()
    knn: sklearn.neighbors.KNeighborsClassifier = load_knn(args.knn)
    print("Loading KNN model took: ", time.time() - start)

    logs = []
    files = glob.glob(os.path.join(args.input_directory, "**/*.flac"), recursive=True)
    print("files found:", files)
    d: dict = {}
    predictions = []
    labels = []
    time_measurements = []
    save_date = datetime.now().strftime("%Y%m%d%H%M")
    for file in files:
        timestamp = datetime.now()
        timestamp = timestamp.strftime("%H:%M:%S")
        start_time = time.time()

        # Audio loading time
        audio_data, sr = soundfile.read(file)
        audio_loading_time = time.time() - start_time

        # Audio processing time
        audio_processing_time_start = time.time()
        data = np.transpose(audio_data)
        # to convert from two channels to mono
        data = np.mean(data, axis=tuple(range(data.ndim - 1)))

        audio_data = resample(data, data.shape[0] // 2)
        audio_data = np.float32(audio_data)

        audio_data = reshape_input_data(audio_data)
        audio_processing_time = time.time() - audio_processing_time_start

        # TFLite inference time
        inference_start_time = time.time()
        interpreter.set_tensor(input_details[0]['index'], audio_data)
        interpreter.set_tensor(input_details[1]['index'], audio_data)
        interpreter.invoke()
        alt = interpreter.get_tensor(output_details[1]['index'])
        tflite_inference_time = time.time() - inference_start_time

        # KNN inference time
        knn_inference_start_time = time.time()
        predicted_class = knn.predict(alt)[0]
        knn_inference_time = time.time() - knn_inference_start_time

        predictions.append(predicted_class)

        if args.eval_mode:
            label = get_class_of_file(file)
            labels.append(label)
            logs.append((file, label, predicted_class))
        else:
            logs.append((file, "unknown", predicted_class))
            d[predicted_class] = d.get(predicted_class, 0) + 1

        total_time = time.time() - start_time

        # Store time measurements as intermediate results
        time_measurements.append((file, audio_loading_time, audio_processing_time,
                                  tflite_inference_time, knn_inference_time, total_time, timestamp))
    if args.eval_mode:
        print("Evaluation mode")
        cm = create_confusion_matrix(labels, predictions)
        print(cm)
        print(classification_report(labels, predictions))
    logs_to_csv(logs)

    # Write time measurements to CSV file
    with open(f'./time_measurements_{save_date}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Audio File', 'Audio Loading Time', 'Audio Processing Time',
                         'TFLite Inference Time', 'KNN Inference Time', 'Total Time', 'Start Time'])
        writer.writerows(time_measurements)

    print(d)


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--model-file", "--m", help="tflite model to be executed",
                                 default="./models/bulbul.tflite")
    argument_parser.add_argument("--knn", "--knn", help="path to pickled knn",
                                 default="./models/knn_5.pkl")
    argument_parser.add_argument("--input-directory", "--i", help="path to input directory")
    argument_parser.add_argument("--eval-mode", "--e", help="evaluation mode", default=0, type=int)

    args = argument_parser.parse_args()
    print(args)

    main(args)