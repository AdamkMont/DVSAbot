from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import boto3
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

#SNS setup
client = boto3.client('sns')

def pub(message):
    client.publish(
        TopicArn='arn:aws:sns:eu-west-2:163692856542:DVSA',
        Message=message
    )

# Ensure that your details are copied into launchDVSA.py to
# quickly login when tests become available

details = {
    "Licence": "MONTG912047AK9EX", # Full UK Licence
    "Booking_Ref": "47478253", # Test Booking Refrence
    "Test_Center": "Edinburgh (Musselburgh)" # Name of Test Center
}



#Headless option
options = Options()
options.headless = True

# Use Chrome for website
driver = webdriver.Chrome(options=options)

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


#Check if any tests avaliable
while True:
    try:
        x=driver.find_element_by_id("main").get_attribute('innerHTML')
    except:
        time.sleep(10)
    break

if "There are no tests available" in driver.find_element_by_id("main").get_attribute('innerHTML'):
    driver.quit()
    print("No test available")
else:
    print("Tests available, checking dates...")

    minDate = datetime.strptime(details["before_date"], "%Y-%m-%d")

    available_calendar = driver.find_element_by_class_name("BookingCalendar-datesBody")
    available_days = available_calendar.find_elements_by_xpath(".//td")
    available_days_msg = ""
    
    for day in available_days:
        if not "--unavailable" in day.get_attribute("class"):
            day_a = day.find_element_by_xpath(".//a")
            if datetime.strptime(day_a.get_attribute("data-date"), "%Y-%m-%d") < minDate:
                print("Available: " + day_a.get_attribute("data-date"))
                available_days_msg = available_days_msg + """
    """+ day_a.get_attribute("data-date")
            
    
    message = """
    Driving tests has become available at """ + details["Test_Center"] + """ on the following days before """ + details["before_date"] + """:
    """ + available_days_msg + """
    
    Click here to launch the DVSA booking website: https://driverpracticaltest.dvsa.gov.uk/manage
    """

    if available_days_msg != "":
        pub(message)
        print("Sent!")
    else:
        print("No preferred dates available")

    driver.quit()


