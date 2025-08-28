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
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, TimeoutException, UnexpectedAlertPresentException
import datetime
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
import threading

downloader_url = "https://cnvmp3.com/v33"
curr_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
driver_loc = os.path.join(curr_dir, 'geckodriver.exe')
downloads_folder_path = "C:/Users/robobrochta/Downloads"
config_file = "config.yaml"
timeout_secs = 5

# spin up chrome @ url
'''
options = webdriver.ChromeOptions() 
#options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get(downloader_url)
'''

# open tor
p = subprocess.Popen("C:/Users/robobrochta/Desktop/Tor Browser/Browser/firefox.exe")
#tor_start_time = datetime.datetime.now().strftime(time_format)
#logger.info(f"{tor_start_time}: tor started")

# selenium initialization
profile = webdriver.FirefoxProfile("C:/Users/robobrochta/Desktop/Tor Browser/Browser/TorBrowser/Data/Browser/profile.default")
options = webdriver.FirefoxOptions()
profile.set_preference("browser.download.dir", downloads_folder_path)
profile.set_preference('profile', "C:/Users/robobrochta/Desktop/Tor Browser/Browser/TorBrowser/Data/Browser/profile.default")
#profile.set_preference('network.proxy.type', 1)
#profile.set_preference('network.proxy.socks', '127.0.0.1')
#profile.set_preference('network.proxy.socks_port', 9051)
#profile.set_preference("network.proxy.socks_remote_dns", False)
profile.update_preferences()
options.profile = profile
service = Service(executable_path = driver_loc)


def reopen_tor(driver, tor_process):
    # closes and reopens tor, webdriver
    ##logger.info("resetting circuit")
    try:
        time.sleep(1.5)
        tor_process.terminate()
        tor_process.kill()
        time.sleep(1.5)
        driver.quit()
    except Exception as e:
        #logger.error(e)
        print(e)


def enterURLAndConvert(song_url, driver):
    driver.refresh()
    #active_downloads_thread = threading.Thread(target=isDownloadComplete, args = (is_initial_launch, ))

    try:
        wait = WebDriverWait(webdriver, timeout_secs)
        # convert & wait for download    
        convert_btn = findElementSafe(driver.find_element(By.ID, "convert-button-1"))
        wait.until(EC.visibility_of(convert_btn))
        # convert_again_btn = findElementSafe(driver.find_element(By.ID, "convert-again-btn"))
        video_info = findElementSafe(driver.find_element(By.ID, "video-info"))

        if video_info is not None and video_info.get_attribute("style") == "display: none;":
            # enter in song url
            print("Entering url and clicking")

            url_box = driver.find_element(By.ID, "video-url")
            url_box.clear()
            url_box.send_keys(song_url)
            wait.until(EC.element_to_be_clickable(convert_btn), timeout_secs)
            print("Downloading in progress...")
            convert_btn.click()

            spinner = findElementSafe(driver.find_element(By.ID, "spinner"))
            countdown = timeout_secs
            while spinner is not None and spinner.get_attribute("style") != "display: none;" and countdown > 0: 
                # if spinner is present, wait for x seconds before redoing this
                time.sleep(timeout_secs)
                countdown -= 1
            
            if countdown == 0:
                print("Likely rate limited, reopening tor...")
                reopen_tor(driver, p)
                driver = webdriver.Firefox(service = service, options=options)
                driver.get(downloader_url)
                enterURLAndConvert(song_url, driver)

            return True

        else:
            print("Need to refresh")
            driver.refresh()
        '''
        else:
            print("Convert again is found")
            wait.until(EC.element_to_be_clickable(convert_again_btn), timeout_secs)
            convert_again_btn.click()

            enterURLAndConvert(song_url)
        '''
        
        #active_downloads_thread.start()
        #active_downloads_thread.join()

    except TimeoutException:
        print("timed out, reloading...")
        enterURLAndConvert(song_url, driver)
        
    except:
        print("Something fucked up, reloading...")
        enterURLAndConvert(song_url, driver)

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
        driver = webdriver.Firefox(service = service, options=options)
        driver.get(downloader_url)
        # read from config
        song_urls = loadConfig()
        url_index = 0
        
        while url_index < len(song_urls):
            print(url_index)
            url = song_urls[url_index]
            enterURLAndConvert(url, driver)

            url_index += 1

            time.sleep(timeout_secs)

  
        print("All downloads complete!")


def isDownloadComplete(isInitialLaunch):

    # wait for .mp3 to completely download before looping again (occurs when part file no longer exists)
    #all_files = getRelevantFiles(downloads_folder_path)
    #print(len(all_files))
    if isInitialLaunch:
        print("initial launch")
    while True:
        spinner = findElementSafe(driver.find_element(By.ID, "spinner"))
        part_files = glob.glob(downloads_folder_path + "\\*.part")
        crdownload_files = glob.glob(downloads_folder_path + "\\*.crdownload")
        if len(part_files) > 0 or len(crdownload_files) > 0:
            print("Downloading in progress...")
        elif isInitialLaunch and len(part_files) == 0 and len(crdownload_files) == 0:
            isInitialLaunch = False
        elif spinner is not None and spinner.get_attribute("style") != "display: none;": 
            # if spinner is present, keep waiting
            print("Likely rate limited, reopening tor...")
            reopen_tor(driver, p)
            driver = webdriver.Firefox(service = service, options=options)

            return True
        else:
            print("Download complete!")
            isInitialLaunch = False
            return True
    

def getRelevantFiles(downloads_folder_path):
    today = datetime.datetime.now().date()
    # get the files on or after today (not before program is run)
    relevant_files = []
    for file in os.listdir(downloads_folder_path):
        filetime = datetime.datetime.fromtimestamp(
                os.path.getctime(f"{downloads_folder_path}\\{file}"))
        if filetime.date() == today:
            relevant_files.append(file)
    return relevant_files

main()