# Develop a command short plugin for DaVinci Platform 

## Usage

* Start local server

```bash
python myserver.py
```

* Record and ASE

```
# browse http://127.0.0.1:5000/start_recording
# press space to stop recording
```


## Installation

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
  wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.runsudo sh cuda_11.8.0_520.61.05_linux.run

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
