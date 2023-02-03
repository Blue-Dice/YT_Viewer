from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from concurrent.futures import ThreadPoolExecutor
from fake_headers import Headers
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from Helpers import ChromeSpoofer
import requests
from requests.exceptions import RequestException
import zipfile
import chromedriver_autoinstaller
import pytube
import json
import platform
import time
import random
import os

class YTViewer():
    
    viewports = ['2560,1440', '1920,1080',
                 '1440,900', '1536,864',
                 '1366,768', '1280,1024',
                 '1024,768']
    referers = ['https://search.yahoo.com/',
                'https://duckduckgo.com/',
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://t.co/',
                'https://www.facebook.com/']
    
    def __init__(self, keep_alive, enable_headless, workers, enable_proxy):
        self.session_count = 1
        self.video_count = 0
        self.status = True
        self.proxy = None
        self.proxy_type = None
        self.workers = workers
        self.auth_required = False
        self.keep_alive = keep_alive
        self.enable_proxy = enable_proxy
        self.enable_headless = enable_headless
        try:
            print('Fetching all video urls...')
            self.playlist = []
            stream_config = json.load(open('stream.json', 'r'))
            for url in stream_config['playlists']:
                self.playlist += pytube.Playlist(url)
            self.playlist += stream_config['videos']
            self.playlength = len(self.playlist)
            print(f'Located {self.playlength} videos')
        except Exception as e:
            self.status = False
            print(f'Error while reading stream configuration -> {e}')
    
    def create_proxy_extension(self):
        self.proxy_path = 'SpooferAgents/IP_spoofing'
        with zipfile.ZipFile(self.proxy_path, 'w') as zp:
            zp.writestr('manifest.json', ChromeSpoofer.manifest_json)
            zp.writestr('background.js', ChromeSpoofer.background_js)
    
    def generate_profile(self):
        header = Headers(
            browser='chrome',
            os=platform.system(),
            headers=False
        ).generate()
        return random.choices(self.viewports), header['User-Agent']
    
    def call_requests(self, url):
        driver = self.create_stealth_session()
        self.stream_video(driver, url)
        driver.quit()
    
    def run(self):
        with ThreadPoolExecutor(max_workers = self.workers) as ex:
            for url in self.playlist:
                ex.submit(self.call_requests, url)
        if self.keep_alive and self.status:
            print(f'Restarting session -> Completed: [{self.session_count}]')
            self.session_count += 1
            self.run()
    
    def spoof_geolocation(self, driver):
        try:
            proxy_dict = {
                'http': f'{self.proxy_type}://{self.proxy}',
                'https': f'{self.proxy_type}://{self.proxy}',
            }
            resp = requests.get('http://ip-api.com/json', proxies=proxy_dict, timeout=30)
            if resp.status_code == 200:
                location = resp.json()
                params = {
                    'latitude': location['lat'],
                    'longitude': location['lon'],
                    'accuracy': random.randint(20, 100)
                }
                driver.execute_cdp_cmd('Emulation.setGeolocationOverride', params)
        except (RequestException, WebDriverException):
            pass
    
    def set_referer(self, driver):
        try:
            referer = random.choice(self.referers)
            driver.get(referer)
        except WebDriverException:
            pass
    
    def create_stealth_session(self):
        if self.status:
            try:
                if not os.path.isdir('chromedriver'):
                    os.mkdir('chromedriver')
                driver_path = chromedriver_autoinstaller.install(path='chromedriver')
                options = ChromeOptions()
                viewport, agent = self.generate_profile()
                if not self.enable_headless:
                    options.add_argument('--headless')
                    options.add_argument('--disable-gpu')
                else:
                    options.add_extension(ChromeSpoofer.WEBRTC_CONTROL_SPOOFER)
                    options.add_extension(ChromeSpoofer.ACTIVITY_SPOOFER)
                    options.add_extension(ChromeSpoofer.FINGERPRINT_SPOOFER)
                    options.add_extension(ChromeSpoofer.TIMEZONE_SPOOFER)
                if self.enable_proxy == 'auth':
                    self.create_proxy_extension()
                    options.add_argument(f'--load-extension={self.proxy_path}')
                elif self.enable_proxy == 'no-auth':
                    options.add_argument(f'--proxy-server={self.proxy_type}://{self.proxy}')
                options.add_argument('--no-sandbox')
                options.add_argument('--mute-audio')
                options.add_argument('--log-level=3')
                options.add_argument('--start-maximized')
                options.add_argument('--disable-web-security')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-blink-features')
                options.add_argument(f'--window-size={viewport[0]}')
                options.add_argument('--disable-features=UserAgentClientHint')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument(f'user-agent={agent}')
                prefs = {'intl.accept_languages': 'en_US,en',
                        'credentials_enable_service': False,
                        'profile.password_manager_enabled': False,
                        'profile.default_content_setting_values.notifications': 2,
                        'download_restrictions': 3}
                options.add_experimental_option('prefs', prefs)
                options.add_experimental_option('extensionLoadTimeout', 120000)
                options.add_experimental_option('useAutomationExtension', False)
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                options.add_experimental_option('excludeSwitches', ['enable-automation'])
                webdriver.DesiredCapabilities.CHROME['loggingPrefs'] = {
                    'driver': 'OFF', 'server': 'OFF', 'browser': 'OFF'
                }
                driver = webdriver.Chrome(service=ChromeService(driver_path), options=options)
                print('Session successfully created')
                if self.enable_proxy == 'no-auth': self.spoof_geolocation(driver)
                self.set_referer(driver)
                return driver
            except Exception as e:
                self.status = False
                print(f'Error while starting chrome driver -> {e}')
    
    def wait_session(self, start_time, seek_time):
        while int(time.time()-start_time) < seek_time:
            pass # bypass linter
    
    def stream_video(self, driver, url):
        if self.status:
            try:
                print(f'Streaming [{url}]')
                driver.get(url)
                time.sleep(3)

                video_length = int(driver.execute_script('return document.getElementsByTagName("video")[0].duration'))
                rand_percent = random.randint(60, 95)
                seek_time = int(video_length * rand_percent / 100)
                
                print(f'Video duration: {video_length} seconds')
                print(f'Video watch time: {seek_time} seconds ({rand_percent}%)')
                
                start_time = time.time()
                play_btn = driver.execute_script('return document.querySelector("[aria-label=Play]")')
                play_btn.send_keys(Keys.ENTER)
                
                self.wait_session(start_time, seek_time)
                
                driver.save_screenshot('screenshot.png')
                self.video_count += 1
                print(f'Finished streaming -> video count: {self.video_count}/{self.playlength}')
            except Exception as e:
                print(f'Error while streaming [{url}] -> {e}')