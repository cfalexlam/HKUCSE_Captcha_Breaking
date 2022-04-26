# import modules
import csv
from cv2 import cv2
import numpy as np
import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import tensorflow as tf
import time
import datetime

# import functions
from functions import prediction

#---------------------------------------------------------------------------------------

# global variables
IMG_FILE = "image.png"
COURTNO = { 
    "SHP2A": 1, "SHP2B": 2, "SHP2C": 3,
    "FHS1": 1, "FHS2": 2, "FHS3": 3, "FHS4": 4}

# account details
UID = "********"
PASSWORD = "********"

#---------------------------------------------------------------------------------------
# initialize prediction model

# use GPU
# physical_devices = tf.config.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(physical_devices[0], True)

# use CPU instead
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# load model
MODEL = tf.keras.models.load_model('captcha/captcha_cnn')

#--------------------------------------------------------------------------------------

# initialize driver
driver = webdriver.Chrome("chromedriver.exe")

def time_in_range():
    """
    Check if current time is between 06:30 and 23:30
    """
    current_time = datetime.datetime.now().time()
    return datetime.time(6, 30, 0) <= current_time < datetime.time(23, 30, 0)

def load_data(file):
    """
    Load details of desired bookings from a CSV file. 
    Remove entries that cannot be booked because bookings can only be made 28 days in advance.
    """    
    entries = []
    today = datetime.date.today()
    current_time = datetime.datetime.now().time() 

    # if time is between 23:30 and 23:59, add one day to today so that bookings can be made 29 days in advance
    if not time_in_range():
        if current_time <= datetime.time(23, 59, 59):
            today = today + datetime.timedelta(days=1)

    with open(file) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            split_date = row[0].split("/")
            date = datetime.date(int(split_date[2]), int(split_date[1]), int(split_date[0]))
            if date - today <= datetime.timedelta(days=28):
                entries.append(tuple(row))

    return sorted(entries, key=lambda x: datetime.datetime.strptime(x[0], "%d/%m/%Y"), reverse=True)

def delay_until_630():
    """
    Check if time is not between 06:30 and 23:30,
    if so, make the program sleep until 06:30
    """

    current_time = datetime.datetime.now().time()

    if not time_in_range():
        print("Program will be scheduled to run at 06:30")
        if current_time <= datetime.time(23, 59, 59):
            # make program sleep until tomorrow 6:30
            seconds_until_630 = (datetime.time(23, 59, 59) - current_time).total_seconds() + 3600 * 6.5
            time.sleep(seconds_until_630)
        else:
            # make program sleep until 6:30 on the same day
            seconds_until_630 = (datetime.time(6, 30, 0) - current_time).total_seconds()
            time.sleep(seconds_until_630)



def login():
    """
    Log on to CSE main page.
    """
    
    driver.get("https://hkuportal.hku.hk/login.html")
    login_form = driver.find_element_by_name("form")
    uid_input = driver.find_element_by_id("username")
    password_input = driver.find_element_by_id("password")

    # login to portal
    uid_input.send_keys(UID)
    password_input.send_keys(PASSWORD)
    login_form.submit()

    # switch to page
    driver.get("https://sis-eportal.hku.hk/psp/ptlprod_newwin/EMPLOYEE/EMPL/e/?url=https%3a%2f%2fbs.cse.hku.hk&FolderPath=PORTAL_ROOT_OBJECT.Z_CAMPUS_INFORMATION_SERVICES.Z_N_SERVICE_DEPARTMENTS.Z_N_IHP.Z_N_SPORTS_FACILITIES_BOOKING&IsFolder=false&IgnoreParamTempl=FolderPath%2cIsFolder")

def book(date, start_time, end_time, team, court):
    """
    Perform the booking action given the booking particulars.
    """
    driver.get("https://bs.cse.hku.hk/ihpbooking/servlet/IHP_Booking/showActivityList")
    driver.execute_script("javascript:goToActivity('{}')".format(team))
    driver.execute_script("javascript:startBooking('{}')".format(date))
    driver.execute_script("javascript:bookThisSlot('{}', '{}', '{}')".format(start_time, court, COURTNO[court]))
    driver.switch_to.alert.accept()

    # select booking (first booking option) and end time
    
    try:
        driver.find_element_by_xpath("/html/body/form/table/tbody/tr[4]/td[2]/input[1]").click()
        Select(driver.find_element_by_name("end_time")).select_by_visible_text(end_time)
        driver.find_element_by_name("form").submit()

        # agree page
        if team == "Squash::1":
            driver.find_element_by_name("no_of_people").send_keys("2")
        driver.find_element_by_name("agree").click()
        driver.find_element_by_name("form").submit()

        # delay the program if outside booking period
        delay_until_630()

    # captcha page (only uncomment when book)
        while True:
            try:
                driver.find_element_by_name("imgCaptcha").screenshot(IMG_FILE)
                driver.find_element_by_id("ansCaptcha").send_keys(prediction(cv2.imread(IMG_FILE, 0), MODEL))
                driver.find_element_by_id("btnSubmit").click()
                if driver.find_element_by_xpath("/html/body/center/font[1]/b").text == "Thank you!":  # booking successful
                    print("You have successfully booked {} for {} on {}, from {} to {}.".format(court, team, date, start_time, end_time))
                    break

            except Exception as e:
                # for debugging purpose
                print(e)

                print("Your attempted booking of {} for {} on {}, from {} to {}, has been unsuccessful, possibly due to time conflicts, or double booking of the same court on the same day, or double booking of two courts by the same person at the same time.".format(court, team, date, start_time, end_time))
                break

    except Exception as e:
        # for debugging purpose
        print(e)

        # if desired time is not available while choosing start_time or end_time, exception arises
        print("Your attempted booking of {} for {} on {}, from {} to {}, has been unsuccessful as the court is no longer available.".format(court, team, date, start_time, end_time))
        
def main():
    
    # load data
    entries = load_data("schedule.csv")

    # log on to CSE main page
    login()

    # start booking
    for date, start_time, end_time, team, court in entries:
        book(date, start_time, end_time, team, court)
    
    driver.close()

if __name__ == "__main__":
    main()
