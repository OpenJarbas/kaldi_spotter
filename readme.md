wake word spotting with kaldi

edit CONFIG in kaldi_spotter.py

# Install

## Raspbian 9 (stretch) on a Raspberry Pi 2/3
```bash
echo "deb http://goofy.zamia.org/repo-ai/raspbian/stretch/armhf/ ./" >/etc/apt/sources.list.d/zamia-ai.list
wget -qO - http://goofy.zamia.org/repo-ai/raspbian/stretch/armhf/bofh.asc | sudo apt-key add -
apt-get update
apt-get install kaldi-chain-zamia-speech-de kaldi-chain-zamia-speech-en python-kaldiasr python-nltools pulseaudio-utils pulseaudio
pip install pyee
```

## Debian 9 (stretch, amd64)
```bash
apt-get install apt-transport-https
echo "deb http://goofy.zamia.org/repo-ai/debian/stretch/amd64/ ./" >/etc/apt/sources.list.d/zamia-ai.list
wget -qO - http://goofy.zamia.org/repo-ai/debian/stretch/amd64/bofh.asc | sudo apt-key add -
apt-get update
apt-get install kaldi-chain-zamia-speech-de kaldi-chain-zamia-speech-en python-kaldiasr python-nltools pulseaudio-utils pulseaudio
pip install pyee
```


## CentOS 7 (amd64)
```bash
cd /etc/yum.repos.d
wget http://goofy.zamia.org/zamia-speech/misc/zamia-ai-centos.repo
yum install kaldi-chain-zamia-speech-de kaldi-chain-zamia-speech-en python-kaldiasr python-nltools pulseaudio-utils pulseaudio
pip install pyee
```


# credits

[zamia-speech](https://github.com/gooofy/zamia-speech)