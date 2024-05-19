#/bin/sh

pip install -r requirements.txt
export PYTHONPATH="${PYTHONPATH}:$PWD"

cd bot && python main.py