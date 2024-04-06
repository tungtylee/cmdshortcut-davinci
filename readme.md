# Develop a command short plugin for DaVinci Platform 

## Usage

* Start local server

```bash
python myserver.py
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
