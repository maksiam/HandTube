import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import numpy as np
from selenium import webdriver
import undetected_chromedriver as us
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pickle
from time import sleep
import os

# Path
path = './cookies.pkl'
# Check whether a path pointing to a file
isFile = os.path.isfile(path)
print(isFile)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=1)
if isFile is False:
    driver = us.Chrome()
    # Open the website
    driver.get(
        'https://accounts.google.com/v3/signin/identifier?dsh=S453020169%3A1670356882062286&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Dru%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F%253FthemeRefresh%253D1&ec=65620&hl=ru&passive=true&service=youtube&uilel=3&flowName=GlifWebSignIn&flowEntry=ServiceLogin&ifkv=ARgdvAt-DFqztq10v9dZNXTMrivBsEVZBdvLXDtAF2Mk26D6FOo0xc7PU4Ugn6ji7xVZXlT5WAh5')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.NAME, 'identifier'))).send_keys(
        f'{"your email"}\n')  # enter email
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.NAME, 'Passwd'))).send_keys(
        f'{"your password"}\n')  # enter password
    sleep(100)  # confirm authentication
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))  # serialize cookies
    # print(driver.get_cookies())
    driver.close()

driver = webdriver.Chrome()
cookies = pickle.load(open("cookies.pkl", "rb"))  # deserialize cookies
driver.get('https://www.youtube.com/')
for cookie in cookies:
    driver.add_cookie(cookie)  # add in current session our cookies
driver.refresh()

# Indicators for gestures
play_button_check = True
next_button_check = True
sound_button_check = True
like_button_check = True
scroll_check = True
scroll_pointer_y = 0
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList, _ = detector.findPosition(img)

    if lmList:
        # print(lmList[8][1])
        count_of_fingers = detector.fingersUp()
        if lmList[8][1] > lmList[5][1] and lmList[12][1] < lmList[9][1] and lmList[16][1] < lmList[13][1] and \
                lmList[20][1] < lmList[17][1] and play_button_check == True:
            play_button = driver.find_element('class name', 'ytp-play-button')
            play_button.click()
            play_button_check = False
        elif lmList[8][1] < lmList[5][1] and lmList[12][1] < lmList[9][1] and lmList[16][1] < lmList[13][1] and \
                lmList[20][1] < lmList[17][1] and play_button_check == False:
            play_button_check = True

        if lmList[8][1] < lmList[5][1] and lmList[12][1] < lmList[9][1] and lmList[16][1] > lmList[13][1] and \
                lmList[20][1] > lmList[17][1] and next_button_check == True:
            next_button = driver.find_element('class name', 'ytp-next-button')
            next_button.click()
            next_button_check = False
        elif lmList[8][1] < lmList[5][1] and lmList[12][1] < lmList[9][1] and lmList[16][1] < lmList[13][1] and \
                lmList[20][1] < lmList[17][1] and next_button_check == False:
            next_button_check = True

        if lmList[8][1] > lmList[5][1] and lmList[12][1] > lmList[9][1] and lmList[16][1] > lmList[13][1] and \
                lmList[20][1] > lmList[17][1] and sound_button_check == True:
            sound_button = driver.find_element('class name', 'ytp-mute-button')
            sound_button.click()
            sound_button_check = False
        elif lmList[8][1] < lmList[5][1] and lmList[12][1] < lmList[9][1] and lmList[16][1] < lmList[13][1] and \
                lmList[20][1] < lmList[17][1] and sound_button_check == False:
            sound_button_check = True

        if count_of_fingers[0] == 0 and count_of_fingers[1:5] == [1, 1, 1, 1]:
            like_button = driver.find_element('class name', 'yt-spec-button-shape-next--segmented-start')
            like_button.click()
            like_button_check = False
            sleep(3)
        elif count_of_fingers == [0, 0, 0, 0, 0]:
            like_button_check = True

        if lmList[8][0] > lmList[5][0] and lmList[12][0] > lmList[9][0] and lmList[16][0] > lmList[13][0] and \
                lmList[20][0] < lmList[17][0] and count_of_fingers[0] == 1 and scroll_check is True:
            scroll_pointer_y += 300
            driver.execute_script("window.scrollTo(0, %d);" % scroll_pointer_y)
            scroll_check = False
        elif lmList[8][0] < lmList[5][0] and lmList[12][0] < lmList[9][0] and lmList[16][0] < lmList[13][0] and \
                lmList[20][0] < lmList[17][0] and count_of_fingers[0] == 1 and scroll_check is False:
            scroll_check = True
    imgNew = np.zeros_like(img, np.uint8)
    out = img.copy()
    alpha = 0.5
    mask = imgNew.astype(bool)
    out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]
    cv2.imshow('Image', out)
    cv2.waitKey(1)
