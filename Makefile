dev:
	virtualenv -p python3 .git/venv3
	.git/venv3/bin/python -m pip install --user --upgrade -r requirements.txt
	touch settings_local.py
