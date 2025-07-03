from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import signal


def wait_for_file_complete(folder_path, timeout=60, poll_interval=1, stable_duration=2):
    print("?? Watching for MP3s in:", folder_path)
    start_time = time.time()

    # Record initial state of folder
    initial_files = set(os.listdir(folder_path))
    candidate = None

    while time.time() - start_time < timeout:
        current_files = set(os.listdir(folder_path))
        new_files = current_files - initial_files

        # Filter to actual .mp3s that aren't partials
        legit_mp3s = [
            f for f in new_files
            if f.endswith(".mp3") and not f.endswith((".part", ".crdownload"))
        ]

        if legit_mp3s:
            candidate = max(
                (os.path.join(folder_path, f) for f in legit_mp3s),
                key=os.path.getctime
            )
            break

        time.sleep(poll_interval)

    if not candidate:
        raise TimeoutError("?? No new MP3 found in folder.")

    print("?????? Found potential file:", os.path.basename(candidate))

    # Watch the file until it stabilizes
    last_size = -1
    stable_start = None

    while time.time() - start_time < timeout:
        try:
            current_size = os.path.getsize(candidate)
        except FileNotFoundError:
            current_size = -1

        if current_size == last_size:
            if stable_start is None:
                stable_start = time.time()
            elif time.time() - stable_start >= stable_duration:
                print("? MP3 ready:", os.path.basename(candidate))
                return os.path.basename(candidate)
        else:
            print(f"? File size changing: {last_size} -> {current_size}")
            last_size = current_size
            stable_start = None

        time.sleep(poll_interval)

    raise TimeoutError("?? File never stabilized. Either bugged or still downloading.")

def download(link):
    service = Service(executable_path="/usr/local/bin/geckodriver")

    options = Options()
    # ?? Uncomment if running on a headless setup
    # options.add_argument("--headless")

    # ?? Add fake user-agent to dodge bot detection
    options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )

    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)  # use custom folder
    profile.set_preference("browser.download.dir", "/home/zeglexa/Desktop/MusicPlayer/Songs")
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")  # or whatever MIME type
    profile.set_preference("pdfjs.disabled", True)

    options.profile = profile

    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    driver.get("https://cnvmp3.com/v25")
    print("Page title:", driver.title)

    # ?? Wait for the input box to exist and send the link
    search_box = wait.until(EC.presence_of_element_located((By.ID, "video-url")))
    time.sleep(1)
    search_box.send_keys(link)
    search_box.send_keys(Keys.ENTER)

    # ?? Wait for the convert/download button to be clickable
    download_btn = wait.until(EC.element_to_be_clickable((By.ID, "convert-button-1")))
    time.sleep(1)
    download_btn.click()

    print("Waiting for download to complete")
    # ?? Optional: wait for download link or finish state if needed
    file_name = wait_for_file_complete("/home/zeglexa/Desktop/MusicPlayer/Songs")

    print("Download should be active now ?")
    time.sleep(6)
    os.system("pkill firefox")
    return file_name
