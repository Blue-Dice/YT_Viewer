import os
from decouple import config

WEBRTC_CONTROL_SPOOFER = os.path.join('SpooferAgents', 'RTC_Control.zip')
ACTIVITY_SPOOFER= os.path.join('SpooferAgents', 'Activity_spoofing.zip')
FINGERPRINT_SPOOFER = os.path.join('SpooferAgents', 'FP_spoofing.zip')
TIMEZONE_SPOOFER = os.path.join('SpooferAgents', 'TZ_spoofing.zip')

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };
chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}
chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (
    config('PROXY_HOST'),
    config('PROXY_PORT'),
    config('PROXY_USER'),
    config('PROXY_PASS')
)