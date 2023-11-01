set -o errexit
set -o pipefail
set -o nounset
shopt -s failglob
set -o xtrace

export DEBIAN_FRONTEND=noninteractive

add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
apt-get install -y python3-distutils build-essential libssl-dev python-dev python3.6 python3.6-dev python3.7 python3.7-dev python3.8 python3.8-dev python3.9 python3.9-dev ffmpeg

curl -sSL https://get.docker.com/ | sh
adduser vagrant docker

curl https://bootstrap.pypa.io/get-pip.py | python3
pip3 install tox tox-docker
