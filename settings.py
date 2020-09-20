import os

# TENCENT
TENCENT_REGION = 'ap-beijing'
TENCENT_SECRET_ID = ''
TENCENT_SECRET_KEY = ''

# Xunfei
XUNFEI_APPID = ''
XUNFEI_ASR_SECRETKEY = ''

if os.path.exists('settings_local.py'):
    from settings_local import *  # NOQA: F401,F403
