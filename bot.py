from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import boto3
import time
from datetime import datetime
from typing import List
import chromedriver_autoinstaller

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

chromedriver_autoinstaller.install()

#SNS setup
client = boto3.client('sns')
sns_topic = client.create_topic("TestTopic")
topic_arn = sns_topic["TopicArn"]

def pub(message):
    client.publish(
        TopicArn=topic_arn,
        Message=message
    )

# Ensure that your details are copied into launchDVSA.py to
# quickly login when tests become available

details = {
    "Licence": "", # Full UK Licence
    "Booking_Ref": "", # Test Booking Refrence
    "Test_Center": " " # Name of Test Center
}

#Headless option
options = Options()
options.headless = True

# Use Chrome for website
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(5)

# Open the test booking management website
driver.get('https://driverpracticaltest.dvsa.gov.uk/login')

# Login with current test details
x = None
while x is None:
    try:
        driver.find_element_by_id("driving-licence-number").send_keys(details["Licence"])
        driver.find_element_by_id("application-reference-number").send_keys(details["Booking_Ref"])
        driver.find_element_by_id("booking-login").click()
        driver.find_element_by_id("test-centre-change").click()
        driver.find_element_by_id("test-centres-input").clear();
        driver.find_element_by_id("test-centres-input").send_keys(details["Test_Center"])
        driver.find_element_by_id("test-centres-submit").click()
        results_container = driver.find_element_by_class_name("test-centre-results")
        test_center = results_container.find_element_by_xpath(".//a")
        test_center.click()
        x=1
    except:
        time.sleep(10)
    break

print('Logged in!')

def get_dates_in_month(driver, max_date: datetime) -> List[datetime]:
    #Find all date elements in current calendar view
    available_calendar = driver.find_element_by_class_name("BookingCalendar-datesBody")
    available_days = available_calendar.find_elements_by_xpath(".//td")
    datetimes_available = []
    
    # For each day in days, check if day is available, 
    # if available, check all available times within day 
    # and return all that are within the requested max date. 
    for day in available_days:
        if not "--unavailable" in day.get_attribute("class"):
            day.find_element_by_class_name('BookingCalendar-dateLink').click()

            timeslots_available = driver.find_elements_by_class_name('SlotPicker-slot-label')
            for timeslot in timeslots_available:
                datetime_available = datetime.strptime(timeslot.get_attribute('data-datetime-label'), '%A, %d %B %y %h:%m %p')
                print(datetime_available)

                if datetime_available < max_date:
                    datetimes_available.append(datetime_available)

    return datetimes_available

months = {'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 
        'october': 10, 'november': 11, 'december': 12}

test_time = datetime(2021, 10, 22, 23, 59, 59)

available_times = []

wait = WebDriverWait(driver, 10)


#Moves to month of requested max day/current test day
#while test_time.month > months[wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "BookingCalendar-currentMonth"))).text.to_lower()]:
#    driver.find_element_by_class_name('BookingCalendar-nav--next').click()

#Begin checking if there are available tests in month
while not driver.find_element_by_id("no-earlier-slots-warn").is_visible():
    available_times_in_month: List[datetime] = get_dates_in_month(driver=driver, max_date=test_time)
    available_times += available_times_in_month

    driver.find_element_by_class_name("BookingCalendar-nav--prev").click()

print(available_times)
print(len(available_times))

message = "Available tests: "
for times in available_times:
    message += times + ". "
pub(message)
