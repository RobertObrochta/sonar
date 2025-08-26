from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import glob
import logging
import subprocess
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
import datetime
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

downloader_url = "https://cnvmp3.com/v33"
curr_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
driver_loc = os.path.join(curr_dir, 'geckodriver.exe')
downloads_folder_path = "C:/Users/robobrochta/Downloads"
config_file = "config.yaml"
timeout_secs = 100

# spin up firefox @ url
driver = webdriver.Firefox()
driver.get(downloader_url)

def enterURLAndConvert(song_url):
    if isDownloadComplete():
        print("Entering url and clicking")
        wait = WebDriverWait(webdriver, timeout_secs)
        # enter in song url
        url_box = driver.find_element(By.ID, "video-url")
        url_box.send_keys(song_url)

        # convert & wait for download    
        convert_btn = findElementSafe(driver.find_element(By.ID, "convert-button-1"))
        try:
            if convert_btn is None:
                wait.until(EC.element_to_be_clickable(convert_btn), timeout_secs)
            convert_btn.click()
        except:
            wait.until(EC.element_to_be_clickable(convert_btn), timeout_secs)
            convert_btn.click()

    else:
        enterURLAndConvert(song_url)


def findElementSafe(element):
    try:
        return element
    except AttributeError:
        print("element not found")
        return None


def createDefaultConfigs():
    print("Adding default settings")

    #TODO implement default settings method
    return


def loadConfig():
    if not os.path.exists(config_file):
        print("Config file doesn't exist, creating...")
        with open(config_file, 'w') as file:
            file.write(f"url_file_path: \'{os.path.join(curr_dir, 'urls.txt')}\'")
            print("Config file created!")
            file.close()

        createDefaultConfigs()
    
    return getSongURLS()


def read_config(config_path):
    stream = open(config_path, 'r')
    configs = yaml.load(stream, Loader=yaml.FullLoader)
    
    return configs


def getSongURLS():
    configs = read_config(config_file)
    url_file = configs['url_file_path']
    song_urls = []

    with open(url_file, 'r') as file:
        all_lines = file.readlines()
        
        for line in all_lines:
            song_urls.append(line.strip())
    
    return song_urls


def main():
    if __name__ == "__main__":
        
        # read from config
        song_urls = loadConfig()
        url_index = 0

        wait = WebDriverWait(webdriver, timeout_secs)

        while url_index < len(song_urls):
            url = song_urls[url_index]
            try:
                print(f"Downloading url: {url}")
                enterURLAndConvert(url)
            except:
                convert_again_btn = findElementSafe(driver.find_element(By.ID, "convert-again-btn"))
                wait.until(EC.element_to_be_clickable(convert_again_btn), timeout_secs)

                if convert_again_btn is not None and convert_again_btn.is_displayed():
                    print(f"Convert again exists")
                    # convert again btn and repeat
                    convert_again_btn.click()
                enterURLAndConvert(url)

            url_index += 1
  
        return


def isDownloadComplete():
    # wait for .mp3 to completely download before looping again (occurs when part file no longer exists)
    all_files = glob.glob(downloads_folder_path + "\\*.mp3")
    if len(all_files) > 0:
        all_files.sort(key=os.path.getmtime, reverse=True)
        while True:
            part_files = glob.glob(downloads_folder_path + "\\*.part")
            print("Downloading in progress...")
            if len(part_files) == 0:
                print("Downloading complete!")
                break
    
    return True


main()