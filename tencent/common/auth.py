import json
import hashlib
import requests
from datetime import datetime

# Tencent SDK
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.asr.v20190614 import asr_client
from tencentcloud.tmt.v20180321 import tmt_client

import settings


def get_asr_auth_client():
    cred = credential.Credential(settings.SECRET_ID, settings.SECRET_KEY)
    httpProfile = HttpProfile()
    httpProfile.endpoint = 'asr.tencentcloudapi.com'
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    clientProfile.signMethod = "TC3-HMAC-SHA256"
    client = asr_client.AsrClient(cred, settings.REGION, clientProfile)

    return client


def get_tmt_auth_client():
    cred = credential.Credential(settings.SECRET_ID, settings.SECRET_KEY)
    httpProfile = HttpProfile()
    httpProfile.endpoint = 'tmt.tencentcloudapi.com'
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    clientProfile.signMethod = "TC3-HMAC-SHA256"
    client = tmt_client.TmtClient(cred, settings.REGION, clientProfile)

    return client


def sign_v3(**kwargs):
    """ Manually make signature instead of using SDK """
    Payload = json.dumps(kwargs.get('Payload'))
    dt = datetime.now()
    RequestTimestamp = dt.timestamp()
    date_str = dt.strftime('%Y-%m-%d')
    CredentialScope = date_str + '/scf/tc3_request'
    Host = kwargs.get('Host')
    Action = kwargs.get('Action')
    Version = kwargs.get('Version')
    Region = kwargs.get('Region') or settings.REGION
    kwargs.update({
        'Payload': Payload,
        'RequestTimestamp': RequestTimestamp,
        'CredentialScope': CredentialScope,
    })
    headers = {
        'Authorization': get_auth_string(**kwargs),
        'Content-Type': 'application/json',
        'Host': Host,
        'X-TC-Action': Action,
        'X-TC-Timestamp': RequestTimestamp,
        'X-TC-Version': Version,
        'X-TC-Region': Region
    }
    resp = requests.post(Host, headers=headers)
    return resp.json()


def get_auth_string(**kwargs):
    # Defaults:
    Algorithm = kwargs.get('Algorithm') or 'TC3-HMAC-SHA256'
    HTTPRequestMethod = kwargs.get('HTTPRequestMethod') or 'POST'
    CanonicalURI = kwargs.get('CanonicalURI') or '/'
    CanonicalQueryString = kwargs.get('CanonicalQueryString') or ''
    SignedHeaders = kwargs.get('SignedHeaders')
    Payload = kwargs.get('payload')
    CredentialScope = kwargs.get('CredentialScope')
    RequestTimestamp = kwargs.get('RequestTimestamp')
    Date = kwargs.get('Date')
    Service = kwargs.get('Service')

    # getCanonicalRequest:
    HashedRequestPayload = hashlib.sha256(Payload).hexdigest().lower()
    CanonicalRequest = '\n'.join([
        HTTPRequestMethod,
        CanonicalURI,
        CanonicalQueryString,
        'content-type;host',
        SignedHeaders,
        HashedRequestPayload,
    ])

    # getStringToSign:
    HashedCanonicalRequest = hashlib.sha256(CanonicalRequest).hexdigest().lower()
    StringToSign = '\n'.join([
        Algorithm,
        RequestTimestamp,
        CredentialScope,
        HashedCanonicalRequest,
    ])
    # getSecretSigning:
    SecretDate = hashlib.sha256(Date, "TC3" + settings.SECRET_KEY).hexdigest().lower()
    SecretService = hashlib.sha256(Service, SecretDate).hexdigest().lower()
    SecretSigning = hashlib.sha256("tc3_request", SecretService).hexdigest().lower()

    # getAuthorization:
    Signature = hashlib.sha256(StringToSign, SecretSigning)
    Authorization = f', Signature={SignedHeaders}, Signature={Signature}'
    Authorization = ', '.join([
        f'{Algorithm} Credential={settings.SECRET_ID}/{CredentialScope}',
        f'SignedHeaders={SignedHeaders}',
        f'Signature={Signature}',
    ])
    return Authorization
