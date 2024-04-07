import os
import queue
import shlex
import subprocess
from threading import Thread

import numpy as np
import simpleaudio as sa
import sounddevice as sd
import soundfile as sf
from flask import Flask, jsonify, request
from flask_cors import CORS
from pynput import keyboard

app = Flask(__name__)
CORS(app)

is_recording = False
is_shortcut = False
fs = 16000  # sampling rate
channels = 2
duration = 60  # max duration
recording = []

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
    global is_recording
    global is_shortcut
    if key == keyboard.Key.space:
        if is_recording:
            stop_queue.put(True)
    if hasattr(key, "char") and key.char == "`":
        if is_shortcut:
            with open("cmd.sh") as f:
                safe_script = f.read()
            subprocess.Popen(["gnome-terminal", "--", "bash", "-c", safe_script])
            print(is_shortcut, "Run shortcut")
    if hasattr(key, "char") and key.char == "~":
        if is_shortcut:
            is_shortcut = False
            print(is_shortcut, "Turn off shortcut")


listener = keyboard.Listener(on_press=on_press)
listener.start()


def callback(indata, frames, time, status):
    # put audio data
    global recording
    recording.extend(indata.copy())


def start_recording():
    global is_recording, recording, stop_queue, recording
    stop_queue = clear_queue(stop_queue)
    is_recording = True
    play_wav("please.wav")
    print("按空白停止錄音，請說")
    recording = []
    print("Recording ...")
    # recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype="int16")
    with sd.InputStream(
        callback=callback, samplerate=fs, channels=channels, dtype="int16"
    ):
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
        np_recording = np.array(recording, dtype=np.int16)
        sf.write(filename, np_recording, fs)
        print(f"Save to {filename}.")
        play_wav("ok.wav")
        print("好的")
        exec_whisper()
    else:
        print("No recording in progress")


def exec_whisper():
    print(WHISPER_CMD)
    os.system(WHISPER_CMD)
    # os.system("gedit recording.wav.txt")


@app.route("/start_recording", methods=["GET", "POST"])
def trigger_recording():
    if not is_recording:
        # Thread(target=start_recording).start()
        start_recording()
        with open("recording.wav.txt") as f:
            questions = f.read()
        return jsonify({"questions": questions}), 200
    else:
        return jsonify({"questions": "Already recording, please retry"}), 200


@app.route("/shortcut", methods=["GET", "POST"])
def shortcut():
    global is_shortcut
    os.system("gedit cmd.sh")
    play_wav("shortcut.wav")
    print("已註冊快捷鍵")
    is_shortcut = True
    with open("cmd.sh") as f:
        safe_script = f.read()

    try:
        return (
            jsonify({"final script": safe_script}),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/execute_bash_script", methods=["POST"])
def execute_bash_script():
    play_wav("execute_bash_script.wav")
    print("執行達哥指令")
    data = request.get_json()
    bash_script = data.get("task")

    with open("cmd_head.sh") as f:
        bash_head = f.read()
    with open("cmd.sh", "w") as f:
        f.write(bash_head + bash_script + "\n")
    os.system("gedit cmd.sh")

    with open("cmd.sh") as f:
        safe_script = f.read()

    if not bash_script:
        return jsonify({"error": "No bash script provided"}), 400
    try:
        # create safe script and block bash
        # create a new terminal window
        subprocess.Popen(["gnome-terminal", "--", "bash", "-c", safe_script])
        return (
            jsonify(
                {"message": "Bash script is being executed in a new terminal window."}
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
