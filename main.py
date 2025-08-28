from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import glob
import logging
import subprocess
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, TimeoutException, UnexpectedAlertPresentException
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
timeout_secs = 5

# spin up chrome @ url
options = webdriver.ChromeOptions() 
driver = webdriver.Chrome(options=options)
driver.get(downloader_url)

def enterURLAndConvert(song_url):
    try:
        if isDownloadComplete():
            wait = WebDriverWait(webdriver, timeout_secs)
            # convert & wait for download    
            convert_btn = findElementSafe(driver.find_element(By.ID, "convert-button-1"))
            convert_again_btn = findElementSafe(driver.find_element(By.ID, "convert-again-btn"))
            video_info = findElementSafe(driver.find_element(By.ID, "video-info"))

            if video_info is not None and video_info.get_attribute("style") == "display: none;":
                # enter in song url
                print("Entering url and clicking")

                url_box = driver.find_element(By.ID, "video-url")
                url_box.clear()
                url_box.send_keys(song_url)
                wait.until(EC.element_to_be_clickable(convert_btn), timeout_secs)
                convert_btn.click()
            else:
                print("Convert again is found")
                wait.until(EC.element_to_be_clickable(convert_again_btn), timeout_secs)
                convert_again_btn.click()

                enterURLAndConvert(song_url)
            
            time.sleep(timeout_secs)
        
        else: 
            enterURLAndConvert(song_url)

    except TimeoutException:
        print("timed out, reloading...")
        driver.refresh()
        enterURLAndConvert(song_url)
        
    except:
        print("Something fucked up, reloading...")
        driver.refresh()
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

        while url_index < len(song_urls):
            print(url_index)
            url = song_urls[url_index]
            enterURLAndConvert(url)

            url_index += 1
  
        print("Downloading complete!")


def isDownloadComplete():
    # wait for .mp3 to completely download before looping again (occurs when part file no longer exists)
    all_files = glob.glob(downloads_folder_path + "\\*.mp3")
    if len(all_files) > 0:
        all_files.sort(key=os.path.getmtime, reverse=True)
        while True:
            part_files = glob.glob(downloads_folder_path + "\\*.part")
            crdownload_files = glob.glob(downloads_folder_path + "\\*.crdownload")
            print("Downloading in progress...")
            if len(part_files) == 0 and len(crdownload_files) == 0:
                print("Downloading complete!")
                break
    
    return True


main()