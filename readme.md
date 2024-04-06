# Develop a command shortcut plugin for DaVinci Platform 

## Usage

* Start local server

```bash
python myserver.py
```

* Record and ASR

```text
# get/post http://127.0.0.1:5000/start_recording
# press space to stop recording

# post http://127.0.0.1:5000/execute_bash_script
# pass json object obj["bash"]
```

## Installation

### Prepare voice hint files (optional)

I use some TTS for generating voice hint files.
Please prepare your wave files, if you need voice hint.

* please.wav: 按空白停止錄音，請說
* execute_bash_script.wav: 執行達哥指令
* ok.wav: 好的
* shortcut.wav: 已註冊快捷鍵

### Prepare python environment

* conda environment and development

```bash
conda create -n cmdshort python=3.11
pip install black
pip install isort
```

* packages

```bash
pip install flask
sudo apt-get install portaudio19-dev
pip install sounddevice --force-reinstall
pip install soundfile
# ImportError: NumPy must be installed for play()/rec()/playrec
pip install numpy
pip install simpleaudio
```

## Whisper Installation

* Clone and Download

```bash
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper
bash ./models/download-ggml-model.sh large-v2
make clean
```

* Setting
  * Install cuda to `/usr/local/cuda`
  * Add path and ld in `~/.bashrc`
  * Modify `Makefile`
  * Build

  ```bash
  # download and install cuda (an example 11.8)
  # you can go to nvidia offical site
  wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
  sudo sh cuda_11.8.0_520.61.05_linux.run

  # ~/.bashrc
  export PATH=/usr/local/cuda/bin:$PATH
  export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

  # Makefile (e.g. sm_86 card)
  # please also refer to issues 876
  # https://github.com/ggerganov/whisper.cpp/issues/876
  CUDA_ARCH_FLAG = sm_86

  # bash command
  make clean
  WHISPER_CUDA=1 make -j
  ```
