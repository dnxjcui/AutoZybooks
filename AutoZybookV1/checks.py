# This file has all the checks implemented, but separated from main for neatness

from datetime import date
from tabnanny import check
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import time

import constants as c

import traceback

def dateCheck(i, dueDateClass, today):
    allDueDates = i.find_element(By.CSS_SELECTOR, dueDateClass).get_attribute('innerHTML')
    formattedDate = ['','','']
    counter = 0

    # Scans date into readable format
    for char in allDueDates:
        if counter == 8:
            break
        if char.isdigit():
            if counter < 2:
                formattedDate[1] += char
            elif counter > 3:
                formattedDate[0] += char
            elif counter > 1:
                formattedDate[2] += char
            counter += 1
    dueDate = date(int(formattedDate[0]), int(formattedDate[1]), int(formattedDate[2]))
    if today < dueDate:
        return True
    else:
        return False

# returns True if incomplete
def pointsCheck(i, pointsClass):
    # Scans points into readable format
    try:
        points = i.find_element(By.CSS_SELECTOR, pointsClass).get_attribute('innerHTML')
    except Exception as e:
        print('There was an error: ')
        print(e)
        return False
    ratioOfPoints = ['', '']
    numerator = True
    for char in points:
        if char == '/':
            numerator = False
        if char.isdigit():
            if numerator == True:
                ratioOfPoints[0] += char
            else:
                ratioOfPoints[1] += char 

    # Compares points and return boolean value
    if int(ratioOfPoints[0]) >= int(ratioOfPoints[1]):
        return False
    else:
        return True

# Returns true if a question or assignment block is incomplete
def checkAnswer(question, type):
    try:
        if type == 'initial':
            try: 
                question.find_element(By.CSS_SELECTOR, c.ASSIGNMENT_INCOMPLETE)
                return True
            except:
                return False

        elif type == 'multipleChoiceInit':
            try: 
                question.find_element(By.CSS_SELECTOR, c.PARTLY_COMPLETE)
                return True
            except:
                return False

        elif type == 'multipleChoice':
            try:
                question.find_element(By.CSS_SELECTOR, c.MULTIPLE_CHOICE_CHECK)
                return False
            except:
                return True
    except Exception as e:
        print("THIS IS BROKEN")
        print('Something went wrong in checkAnswer')
        print(e)
        return False

# This function scans the webpage for answerable questions and then answers them
# Note that lists of elements are often rediscovere to prevent elements from becoming stale
def answerQuestions(animationAssignments, multipleChoiceQuestions, REAL, driver):
    actions = ActionChains(driver)
    try:
        # For each question block(s) container in list multipleChoiceQuesitons, check if it's answered or a test
        for i in multipleChoiceQuestions:
            if checkAnswer(i, 'multipleChoiceInit') or not REAL:
                questionBlocks = i.find_elements(By.CSS_SELECTOR, c.MULTIPLE_CHOICE_QUESTION)

                # For each individual question in a block, get all options and click them until right
                for question in range(len(questionBlocks)):
                    
                    inputs = questionBlocks[question].find_elements(By.TAG_NAME, 'input')

                    # For each input option, click it until correct shows up
                    for option in range(len(inputs)):
                        actions.move_to_element(inputs[option]).click().perform()

                        time.sleep(.2)
    
                        questionBlocks = i.find_elements(By.CSS_SELECTOR, c.MULTIPLE_CHOICE_QUESTION)
                        continueCheck = checkAnswer(questionBlocks[question], 'multipleChoice')
                        # If checkAnswer returns false, it breaks the loop
                        if not continueCheck:
                            break

        time.sleep(10)
        for i in animationAssignments:
            if checkAnswer(i, 'intial') or not REAL:
                doubleSpeed = i.find_element(By.CSS_SELECTOR, c.ANIMATION_2X)
                initStart = i.find_element(By.CSS_SELECTOR, c.ANIMATION_START)
                actions.move_to_element(doubleSpeed).click().perform()
                actions.move_to_element(initStart).click().perform()
                button = i.find_element(By.CSS_SELECTOR, c.ANIMATION_BUTTON)
                while checkAnswer(i, 'inital'):
                    time.sleep(1)
                    try:
                        play = button.find_element(By.CSS_SELECTOR, c.ANIMATION_PLAY).click()
                        actions.move_to_element(play).click().perform()
                    except:
                        pass
    except Exception as e:
        print("Something went wrong in answerQuestions")
        print(e)
        print(traceback.format_exc())
        return False