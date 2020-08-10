import os

REGION = 'ap-beijing'
SECRET_ID = ''
SECRET_KEY = ''

if os.path.exists('settings_local.py'):
    from settings_local import *  # NOQA: F401,F403
