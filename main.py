from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import glob
import logging
import subprocess
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime

downloader_url = "https://cnvmp3.com/v33"
curr_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
driver_loc = os.path.join(curr_dir, 'geckodriver.exe')
downloads_folder_path = "C:/Users/robobrochta/Downloads"

# spin up firefox @ url
driver = webdriver.Firefox()
driver.get(downloader_url)

def enterURLAndConvert(song_url):
    print("Entering url and clicking")
    wait = WebDriverWait(webdriver, 6000)
    # enter in song url
    url_box = driver.find_element(By.ID, "video-url")
    url_box.send_keys(song_url)

    # convert & wait for download    
    convert_btn = driver.find_element(By.ID, "convert-button-1")
    wait.until(EC.element_to_be_clickable(convert_btn))

    convert_btn.click()

def main():
    if __name__ == "__main__":

        #TODO read from file
        song_url = ["https://www.youtube.com/watch?v=OIJ8TmIiEAU", "https://www.youtube.com/watch?v=OIJ8TmIiEAU"]
        
        for url in song_url:
            print(f"Downloading url: {url}")
            donate_btn = driver.find_elements(By.ID, "donate-btn").size > 0
            if donate_btn:
                print(f"Convert again exists")
                # convert again btn and repeat
                wait = WebDriverWait(webdriver, 6000)
                convert_again_btn = driver.find_element(By.ID, "convert-again-btn")
                wait.until(EC.element_to_be_clickable(convert_again_btn))
                if isDownloadComplete:
                    convert_again_btn.click()

            enterURLAndConvert(url)
  
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
                return True

main()