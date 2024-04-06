from threading import Thread

import sounddevice as sd
import soundfile as sf
from flask import Flask, jsonify

app = Flask(__name__)

is_recording = False
recording = None
fs = 44100  # sampling rate
duration = 60  # max duration


def start_recording():
    global is_recording, recording
    is_recording = True
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype="int16")
    print("Recording ...")


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


@app.route("/stop_recording", methods=["GET", "POST"])
def handle_stop():
    stop_recording_and_save()
    return jsonify({"status": "Recording stopped and saved"}), 200


if __name__ == "__main__":
    app.run(debug=True)
