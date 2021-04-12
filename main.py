from selenium import webdriver

import pandas as pd
import csv

import time

CHROMEDRIVER_PATH = "C:/Users/Alex Lam/Desktop/MBBS III/CSE Project/chromedriver.exe"

LOGIN_URL = "https://hkuportal.hku.hk/login.html"
UID = "calexlam"
PASSWORD = "al26529833"


driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH)
driver.get(LOGIN_URL)

login_form = driver.find_element_by_name("form")
uid_input = driver.find_element_by_id("username")
password_input = driver.find_element_by_id("password")


uid_input.send_keys(UID)
password_input.send_keys(PASSWORD)
login_form.submit()

driver.get("https://sis-eportal.hku.hk/psp/ptlprod_newwin/EMPLOYEE/EMPL/e/?url=https%3a%2f%2fbs.cse.hku.hk&FolderPath=PORTAL_ROOT_OBJECT.Z_CAMPUS_INFORMATION_SERVICES.Z_N_SERVICE_DEPARTMENTS.Z_N_IHP.Z_N_SPORTS_FACILITIES_BOOKING&IsFolder=false&IgnoreParamTempl=FolderPath%2cIsFolder")
driver.get("https://bs.cse.hku.hk/ihpbooking/servlet/IHP_Booking/showActivityList")
driver.execute_script("javascript:goToActivity('Hockey_Half::1')")

"""
from datetime import timedelta, date

start_date = date.today()
end_date = start_date + timedelta(28)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

df = []

for date in daterange(start_date, end_date):
    driver.execute_script("javascript:startBooking({})".format(date.strftime("'%d/%m/%Y'")))

    timeslot = driver.find_elements_by_css_selector("table[border='1']")
    rows = timeslot[2].find_elements_by_xpath(".//*[self::tr]")

    time = []
    p2a = []
    p2b = []
    p2c = []

    for row in rows:
        row_elements = row.find_elements_by_xpath(".//*[self::td]")
        time.append(row_elements[0].text)
        p2a.append(row_elements[1].text)
        p2b.append(row_elements[2].text)
        p2c.append(row_elements[3].text)
    
    d = {}
    d["Time"] = time
    d["P2A"] = p2a
    d["P2B"] = p2b
    d["P2C"] = p2c
    df = pd.DataFrame(data=d)
    df.to_csv("C:/Users/Alex Lam/Desktop/MBBS III/CSE Project/Timeslots/{}.csv".format(date.strftime("%d%m%Y")))
"""
		