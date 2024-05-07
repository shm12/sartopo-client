import base64
import hmac
import hashlib
import time
import json
import requests
from urllib.parse import urlparse
from urllib.parse import quote as url_encode

class MyAuth(requests.auth.AuthBase):
    def __init__(self, auth_key, auth_id, online=True):
        self.auth_key = auth_key
        self.auth_id = auth_id
        self.online = online

    def __call__(self, r):
        if self.online:
            return self.online_auth(r)

        # TODO: local auth

    def online_auth(self, r):
        path = urlparse(r.url).path
        expire = int(time.time() * 1000) + 300000

        # embed json into body so we don't need to decide where it resides (json or data)
        payload = r.body.decode() if r.body else ''

        params = {
            'id': self.auth_id,
            'json': payload,
            'expires': str(expire),
            'signature': api_sign(self.auth_key, r.method, path, expire, payload)
        }
        r.prepare_url(r.url, params)

        return r

# ---------------------------------------------------------------------------------------- #
# ----------------- DO NOT TOUCH!! converted to python from sartopo APK  ----------------- #
# ---------------------------------------------------------------------------------------- #

def api_sign(auth_key, method, uri, expire, payload):
    try:
        payload = "" if payload is None else payload
        message = f"{method} {uri}\n{expire}\n{payload}"
        signature = hmac.new(base64.b64decode(
            auth_key), message.encode(), hashlib.sha256).digest()
        return base64.b64encode(signature).decode()
    except Exception as e:
        print(e)
        return ""


def generate_signed_api_url(method, host, uri, payload_json, auth_key, auth_id):
    payload = "" if payload_json is None else json.dumps(payload_json)
    expire = int(time.time() * 1000) + 300000
    api_sign_result = api_sign(auth_key, method, uri, expire, payload)
    if uri.startswith("/") and host.endswith("/"):
        uri = uri[1:]
    return (host + uri, f"json={url_encode(payload)}&id={url_encode(auth_id)}&expires={url_encode(str(expire))}&signature={url_encode(api_sign_result)}")

