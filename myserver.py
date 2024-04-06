import queue
from threading import Thread

import sounddevice as sd
import soundfile as sf
from flask import Flask, jsonify
from pynput import keyboard

app = Flask(__name__)

is_recording = False
recording = None
fs = 44100  # sampling rate
duration = 60  # max duration


# a queue for stopping recording
stop_queue = queue.Queue(maxsize=1)


def clear_queue(q):
    while not q.empty():
        try:
            q.get_nowait()
        except queue.Empty:
            break


def on_press(key):
    global stop_queue
    if key == keyboard.Key.space:
        stop_queue.put(True)


listener = keyboard.Listener(on_press=on_press)
listener.start()


def start_recording():
    global is_recording, recording, stop_queue
    clear_queue(stop_queue)
    is_recording = True
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype="int16")
    print("Recording ...")
    try:
        stop_queue.get(timeout=duration)  # wait key
    except queue.Empty:
        # max duration
        pass
    finally:
        print("Recording st opped.")
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
    else:
        print("No recording in progress")


@app.route("/start_recording", methods=["GET", "POST"])
def trigger_recording():
    if not is_recording:
        Thread(target=start_recording).start()
        return jsonify({"status": "Recording started"}), 200
    else:
        return jsonify({"status": "Already recording"}), 200


if __name__ == "__main__":
    app.run(debug=True)
