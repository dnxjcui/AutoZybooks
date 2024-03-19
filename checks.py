# This file has all the checks implemented, but separated from main for neatness

from datetime import date
# from tabnanny import check
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import time

import constants as c

import traceback

# Checks date and returns True if assignment due date is in the future, false otherwise
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
    if today <= dueDate:
        return True
    else:
        return False

# returns True if points do not match up, false if they do
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

# Returns true if a question or assignment block is incomplete via looking for elements
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

        elif type == 'animation':
            try:
                question.find_element(By.CSS_SELECTOR, c.ANIMATION_PLAY)
                try:
                    question.find_element(By.CSS_SELECTOR, c.ANIMATION_COMPLETE)
                    return False
                except:
                    return True

            except:
                return False


    except Exception as e:
        print('Something went wrong in checkAnswer')
        print(e)
        return False

# This function scans the webpage for answerable questions and then answers them
# Note that the lists of questionBlocks is often redefined to prevent elements from becoming stale
def answerMultipleChoice(questionBlocks, actions, question, i):
    try:
        inputs = questionBlocks[question].find_elements(By.TAG_NAME, 'input')

        # For each input option, click it until correct shows up
        for option in range(len(inputs)):
            actions.move_to_element(inputs[option]).click().perform()

            time.sleep(.2)

            questionBlocks = i.find_elements(By.CSS_SELECTOR, c.MULTIPLE_CHOICE_QUESTION)

            continueCheck = checkAnswer(questionBlocks[question], 'multipleChoice')

            # If checkAnswer returns false, it breaks the loop
            if not continueCheck:
                return

    except Exception as e:
        print("Something went wrong in answerMultipleChoiceQuestions")
        print(e)
        print(traceback.format_exc())
        return False

# Completes the animation assignments
def completeAnimation(animationAssignments, REAL, driver, actions):
    animationAssignments = driver.find_elements(By.CSS_SELECTOR, c.PARTICIPATION_ANIMATION)
    for i in animationAssignments:
        try:
            if (checkAnswer(i, 'initial') or not REAL):
                doubleSpeed = i.find_element(By.CSS_SELECTOR, c.ANIMATION_2X)
                initStart = i.find_element(By.CSS_SELECTOR, c.ANIMATION_START)
                actions.move_to_element(doubleSpeed).click().perform()
                actions.move_to_element(initStart).click().perform()
                time.sleep(.1)
        except:
            if checkAnswer(i, 'animation'):
                play = i.find_element(By.CSS_SELECTOR, c.ANIMATION_PLAY)
                actions.move_to_element(play).click().perform()
    return

# Answers each question
def answerQuestions(animationAssignments, multipleChoiceQuestions, REAL, driver):
    actions = ActionChains(driver)

    # First starts on the animation assignments and lets them run while doing multiple choice 
    # questions to optimize time management.
    completeAnimation(animationAssignments, REAL, driver, actions)

    time.sleep(.2)

    multipleChoiceQuestions = driver.find_elements(By.CSS_SELECTOR, c.PARTICIPATION_MULTIPLE_CHOICE)

    # Answers each multiple choice question while periodically checking animation assignments to do those again. 
    for i in multipleChoiceQuestions:
        if checkAnswer(i, 'multipleChoiceInit') or not REAL:
            questionBlocks = i.find_elements(By.CSS_SELECTOR, c.MULTIPLE_CHOICE_QUESTION)

            # For each individual question in a block, get all options and click them until right
            for question in range(len(questionBlocks)):

                answerMultipleChoice(questionBlocks, actions, question, i)
                if question % 2 == 1:
                    animationAssignments = driver.find_elements(By.CSS_SELECTOR, c.PARTICIPATION_ANIMATION)
                    completeAnimation(animationAssignments, REAL, driver, actions)

                    time.sleep(.1)

    # Loop through animation assignments until they are all complete. Often redeclares
    # the list of animation assignments, because some of them aren't loaded until others are completed.
    while True:
        time.sleep(1)
        completedAnimationAssignments = driver.find_elements(By.CSS_SELECTOR, c.ANIMATION_COMPLETE)

        # Checks to see if assignments are all complete.
        if len(animationAssignments) == len(completedAnimationAssignments):
            break

        else:
            animationAssignments = driver.find_elements(By.CSS_SELECTOR, c.PARTICIPATION_ANIMATION)
            completeAnimation(animationAssignments, REAL, driver, actions)

        # Checks if all assignments are complete again, but it uses a different element that the
        # previous statement could not cover.
        counter = 0
        for i in animationAssignments:
            try: 
                i.find_element(By.CSS_SELECTOR, c.ASSIGNMENT_COMPLETE)
                counter += 1
            except:
                pass
        if len(animationAssignments) == counter:
            break