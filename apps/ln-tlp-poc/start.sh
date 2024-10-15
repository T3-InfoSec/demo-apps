pip install -r alice/requirements.txt
sleep 1
pip install -r bob/requirements.txt
python3 ./bob/setup.py
sleep 2
python3 ./bob/app.py
sleep 5
python3 ./alice/setup.py
sleep 2
python3 ./alice/app.py
