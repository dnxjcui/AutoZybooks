# Author: Nick Cui, lening.n.cui@vanderbilt.edu
# 2022

# Selenium for accessing and interacting with the web
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.\
    options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from pynput.keyboard import Key, Controller

# This is an attempt to disable chrome from asking "are you sure you want to leave this page?"
# every damn second. However, it doesn't work, but I have it here just in case it decides to
# work some day in the distant future.
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option('excludeSwitches', ['disable-popup-blocking'])

# This works around the chrome popup by pressing enter to just accept it.
keyboard = Controller()
keyboard.press(Key.enter)
keyboard.release(Key.enter)

import traceback

# Time for waiting for pages to load
import time

from datetime import date

from checks import dateCheck, pointsCheck, answerQuestions

from sys import argv

# Imports file with helper functions.
import constants as c

# Assumes the program is being run as real and not as a test.
REAL = True
def main(argv):
    # Checks options but I don't understand getopt
    try:
        if argv[1] == '-t' or '-test':
            REAL = False
    except:
        REAL = True
        pass
    
    login = {}
    # Reads in login information
    with open('login_info.txt', 'r') as f:
        login['username'] = f.readline().strip()
        login['password'] = f.readline()
        f.readline()
        driverPath = f.readline().strip()


    # Creates webdriver and goes to link
    # driver = webdriver.Chrome(executable_path = driverPath, options = chrome_options)
    driver = webdriver.Chrome(options = chrome_options)
    driver.get(c.LINK)
    # actions = ActionChains(driver)

    # All time.sleeps in the program are meant to let the page load before the program takes further action
    time.sleep(1)

    # Initializes toDoList with hyperlinks
    toDoList = []

    try:

        # Logs in
        inputs = driver.find_elements(By.CSS_SELECTOR, 'input.'
                                                       'zb-input')


        inputs[0].send_keys(login['username'])
        inputs[1].send_keys(login['password'])
        driver.find_element(By.CSS_SELECTOR, 'button.zb-button.primary.raised.full-width.signin-button').click()

        time.sleep(7)

        # Looks for assignments tab and clicks on it
        sidePanel = driver.find_element(By.CSS_SELECTOR, 'div.zb-card.zybook-panel.ember-view')
        tabs = sidePanel.find_elements(By.CSS_SELECTOR, 'button.full-tab.inactive')
        for i in tabs:
            label = i.find_element(By.CSS_SELECTOR, 'p.label')
            if label.get_attribute('innerHTML') == 'Assignments':
                label.click()
                break

        assignments = sidePanel.find_elements(By.CSS_SELECTOR, c.ASSIGNMENT_CONTAINER)
        today = date.today()

        # Checks each section in each assignment
        for x in range(len(assignments)):
            assignments = sidePanel.find_elements(By.CSS_SELECTOR, c.ASSIGNMENT_CONTAINER)
            try:
                assignmentName = assignments[x].find_element(By.CSS_SELECTOR, c.ASSIGNMENT_TITLE).get_attribute('innerHTML')
            except:
                pass
            # Compares points if real and prints out actual statement
            if not pointsCheck(assignments[x], c.CHAPTER_POINTS) and REAL:
                print('No work to be done on ' + assignmentName)

            # Compares date and points if real and either skips to next assignment or does nothing
            if dateCheck(assignments[x], c.CHAPTER_DUE_DATE, today) and pointsCheck(assignments[x], c.CHAPTER_POINTS) or not REAL:
                assignments[x].click()
                time.sleep(.4)
                sections = sidePanel.find_elements(By.CSS_SELECTOR, c.SECTION_NAME)

                for assignments[x] in sections:
                    if pointsCheck(assignments[x], c.SECTION_POINTS) or not REAL:
                        if not REAL:
                            toDoList.append(assignments[x].find_element(By.CSS_SELECTOR, c.SECTION_LINK).get_attribute('href'))
                            #toDoList.insert(0, assignments[x].find_element(By.CSS_SELECTOR, c.SECTION_LINK).get_attribute('href'))
                        elif REAL:
                            toDoList.append(assignments[x].find_element(By.CSS_SELECTOR, c.SECTION_LINK).get_attribute('href'))
                    time.sleep(.2)
                sidePanel.find_element(By.CSS_SELECTOR, 'i.zb-icon.material-icons.med.secondary').click()
                time.sleep(.05)

            time.sleep(.2)

        # Loops through each link in the list and completes respective assignments by calling on
        # helper functions.
        for i in toDoList:
            driver.get(i)
            if i != 0:
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                except:
                    print("routed to keyboard")
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)
            time.sleep(6)
            animationAssignments = driver.find_elements(By.CSS_SELECTOR, c.PARTICIPATION_ANIMATION)
            multipleChoiceQuestions = driver.find_elements(By.CSS_SELECTOR, c.PARTICIPATION_MULTIPLE_CHOICE)
            answerQuestions(animationAssignments, multipleChoiceQuestions, REAL, driver)
            time.sleep(.5)
    except:
        print("Something went wrong in main")
        print(traceback.format_exc())
        driver.close()

main(argv)

