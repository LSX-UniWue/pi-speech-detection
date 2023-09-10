import argparse
import csv
import time
import pickle
import os

import sklearn.neighbors
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tflite_runtime.interpreter as tflite
import soundfile as sf
import numpy as np
from scipy.signal import resample


class Watcher:

    def __init__(self, out_dir: str, model_file: str, knn_file: str, directory_to_watch: str, move_files: int):
        self.out_dir = out_dir
        self.MODEL_FILE = model_file
        self.KNN_FILE = knn_file
        self.DIRECTORY_TO_WATCH = directory_to_watch
        self.observer = Observer()
        self.move_files = bool(move_files)

        print("Watcher initialized")

    def run(self):
        os.makedirs(self.out_dir, exist_ok=True)
        event_handler = Handler(model_file=self.MODEL_FILE, knn_file=self.KNN_FILE, out_dir=self.out_dir,
                                move_files=self.move_files)
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(2)
        except Exception as e:
            print(e)
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    def __init__(self, model_file: str, knn_file: str, out_dir: str, move_files: bool):

        self.interpreter = tflite.Interpreter(model_path=model_file)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.knn: sklearn.neighbors.KNeighborsClassifier = self.__load_knn(path_to_knn=knn_file)
        self.out_dir = out_dir
        self.move_files = move_files

    def log_prediction(self, filepath: str, predicted_class: int, audio_loading_time: float, knn_time: float,
                       inference_time: float):
        basename = os.path.basename(filepath)
        with open(os.path.join(self.out_dir, "prediction_logs.csv"), 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([basename, predicted_class, audio_loading_time, knn_time, inference_time])

    def on_any_event(self, event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            if event.src_path.endswith(".flac"):
                print("Received created event - %s." % event.src_path)
                predicted_class, audio_loading_time, knn_time, tflite_inference_time = self.__handle_prediction(
                    path_to_audio=event.src_path)
                print(f"Predicted class {predicted_class} for file {event.src_path}.")
                self.log_prediction(filepath=event.src_path, predicted_class=predicted_class,
                                    audio_loading_time=audio_loading_time, knn_time=knn_time,
                                    inference_time=tflite_inference_time)
                # delete audio file from the temporary file system if it contains human speech
                if predicted_class == 1:
                    os.remove(event.src_path)
            else:
                print("Not a flac file: ", event.src_path)

    def __handle_prediction(self, path_to_audio):
        try:
            audio, audio_loading_time = self.__handle_audio_loading(path_to_audio=path_to_audio)

            inference_start_time = time.time()
            self.interpreter.set_tensor(self.input_details[0]['index'], audio)
            self.interpreter.set_tensor(self.input_details[1]['index'], audio)

            self.interpreter.invoke()

            output_data = self.interpreter.get_tensor(self.output_details[1]['index'])
            tflite_inference_time = time.time() - inference_start_time

            knn_start_time = time.time()
            predicted_class = self.knn.predict(output_data)[0]
            knn_time = time.time() - knn_start_time

            # del audio
            del output_data

            return predicted_class, audio_loading_time, knn_time, tflite_inference_time
        except RuntimeError as e:
            print(e)
            return -1, -1, -1, -1

    def __handle_audio_loading(self, path_to_audio: str):
        start_time = time.time()
        audio_data, _ = sf.read(path_to_audio)
        audio_loading_time = time.time() - start_time

        data = np.transpose(audio_data)
        # to convert from two channels to mono
        data = np.mean(data, axis=tuple(range(data.ndim - 1)))

        audio_data = resample(data, data.shape[0] // 2)
        audio_data = np.float32(audio_data)
        audio_data = self.__reshape_input_data(audio_data)
        return audio_data, audio_loading_time

    def __reshape_input_data(self, data):
        data = np.expand_dims(data, axis=0)
        return np.expand_dims(data, axis=-1)

    def __load_knn(self, path_to_knn: str):
        with open(path_to_knn, 'rb') as f:
            knn = pickle.load(f)
        return knn


if __name__ == '__main__':
    args = argparse.ArgumentParser()

    args.add_argument("--out-dir", type=str)
    args.add_argument("--dir-to-watch", type=str)
    args.add_argument("--model-file", type=str, default="./models/bulbul.tflite")
    args.add_argument("--knn-file", type=str, default="./models/knn_5.pkl")
    args = args.parse_args()
    w = Watcher(out_dir=args.out_dir, model_file=args.model_file, knn_file=args.knn_file,
                directory_to_watch=args.dir_to_watch, move_files=args.move_file)
    w.run()
