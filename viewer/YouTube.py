import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
from selenium_stealth import stealth
import pytube
import json
import time
import random
import os
from decouple import config

class YTViewer():
    keep_alive = True
    
    def __init__(self):
        try:
            self.playlist = []
            stream_config = json.load(open('stream.json', 'r'))
            for url in stream_config['playlists']:
                self.playlist += pytube.Playlist(url)
            self.playlist += stream_config['videos']
            self.playlength = len(self.playlist)
            print(f'Located {self.playlength} videos')
        except Exception as e:
            self.keep_alive = False
            print(f'Error while reading stream configuration -> {e}')
    
    def create_stealth_session(self):
        if self.keep_alive:
            if not os.path.isdir('chromedriver'):
                os.mkdir('chromedriver')
            driver_path = chromedriver_autoinstaller.install(path='chromedriver')
            options = ChromeOptions()
            if config('HEADLESS', cast=bool):
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument("--start-maximized")
            options.add_argument('--disable-blink-features')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            self.driver = webdriver.Chrome(service=ChromeService(driver_path), options=options)
            stealth(
                self.driver,
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                languages=["en-GB","en-US", "en"],
                vendor="Google Inc.",
                platform="Linux x86_64",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                run_on_insecure_origins=True,
            )
    
    def create_undetected_session(self):
        if self.keep_alive:
            try:
                options = ChromeOptions()
                if config('HEADLESS', cast=bool):
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--start-maximized')
                self.driver = uc.Chrome(options=options)
                print('Session successfully created')
            except Exception as e:
                self.keep_alive = False
                print(f'Error while starting chrome driver -> {e}')
    
    def destroy_session(self):
        try:
            self.driver.quit()
            print('Session successfully destroyed')
        except Exception:
            print('Error while destroying session')
    
    def stream_video(self):
        video_count = 0
        for url in self.playlist:
            if self.keep_alive:
                try:
                    print(f'Streaming [{url}]')
                    self.driver.get(url)
                    time.sleep(3)

                    video_length = int(self.driver.execute_script('return document.getElementsByTagName("video")[0].duration'))
                    rand_percent = random.randint(60, 95)
                    seek_time = int(video_length * rand_percent / 100)
                    
                    print(f'Video duration: {video_length} seconds')
                    print(f'Video watch time: {seek_time} seconds ({rand_percent}%)')

                    play_btn = self.driver.execute_script('return document.querySelector("[aria-label=Play]")')
                    play_btn.send_keys(Keys.ENTER)
                    time.sleep(seek_time)
                    video_count += 1
                    print(f'Finished streaming -> video count: {video_count}/{self.playlength}')
                except Exception as e:
                    print(f'Error while streaming [{url}] -> {e}')
                    self.keep_alive = False
                    continue