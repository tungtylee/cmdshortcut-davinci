import os
import queue
from threading import Thread

import simpleaudio as sa
import sounddevice as sd
import soundfile as sf
from flask import Flask, jsonify
from pynput import keyboard

app = Flask(__name__)

is_recording = False
recording = None
fs = 16000  # sampling rate
duration = 60  # max duration
WHISPER_M = "./whisper.cpp/main -m ./whisper.cpp/models/ggml-large-v2.bin"
WHISPER_F = " -f recording.wav -otxt recording.txt"
WHISPER_CMD = WHISPER_M + WHISPER_F

# a queue for stopping recording
stop_queue = queue.Queue(maxsize=1)


def play_wav(file_path):
    try:
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    except FileNotFoundError:
        print(f"File missing {file_path}")
    except Exception as e:
        print(f"Error playing file: {e}")


def clear_queue(q):
    while not q.empty():
        try:
            q.get_nowait()
        except queue.Empty:
            break
    return q


def on_press(key):
    global stop_queue
    if key == keyboard.Key.space:
        stop_queue.put(True)
        print("put True")


listener = keyboard.Listener(on_press=on_press)
listener.start()


def start_recording():
    global is_recording, recording, stop_queue
    # stop_queue = clear_queue(stop_queue)
    is_recording = True
    play_wav("please_ailab.wav")

    print("Recording ...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype="int16")
    try:
        stop_queue.get(timeout=duration)  # wait key
    except queue.Empty:
        # max duration
        pass
    finally:
        print("Recording stopped.")
        stop_recording_and_save()


def stop_recording_and_save():
    global is_recording, recording
    if is_recording:
        is_recording = False
        sd.stop()
        # save
        filename = "recording.wav"
        sf.write(filename, recording, fs, subtype="PCM_16")
        print(f"Save to {filename}.")
        play_wav("ok_ailab.wav")
        exec_whisper()
    else:
        print("No recording in progress")


def exec_whisper():
    print(WHISPER_CMD)
    os.system(WHISPER_CMD)
    os.system("gedit recording.wav.txt")


@app.route("/start_recording", methods=["GET", "POST"])
def trigger_recording():
    if not is_recording:
        Thread(target=start_recording).start()
        return jsonify({"status": "Recording started"}), 200
    else:
        return jsonify({"status": "Already recording"}), 200


@app.route("/stop_recording", methods=["GET", "POST"])
def handle_stop():
    stop_recording_and_save()
    return jsonify({"status": "Recording stopped and saved"}), 200


if __name__ == "__main__":
    app.run(debug=True)
