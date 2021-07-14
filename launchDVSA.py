from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


details = {
    "Licence": "MONTG912047AK9EX", # Full UK Licence
    "Booking_Ref": "47478253", # Test Booking Refrence
    "Test_Center": "Edinburgh (Musselburgh)" # Name of Test Center
}

#Headless option
options = Options()
options.headless = True
# Open Chrome
driver = webdriver.Chrome(options=options)

# Open the test management website and login
driver.get('https://driverpracticaltest.dvsa.gov.uk/login')
while True:
    try:
        driver.find_element_by_id("driving-licence-number").send_keys(details["Licence"])
        driver.find_element_by_id("application-reference-number").send_keys(details["Booking_Ref"])
        driver.find_element_by_id("booking-login").click()
        driver.find_element_by_id("test-centre-change").click()
        driver.find_element_by_id("test-centres-input").clear();
        driver.find_element_by_id("test-centres-input").send_keys(details["Test_Center"])
        driver.find_element_by_id("test-centres-submit").click()
    except:
        time.sleep(10)
    break


# Select first test center
results_container = driver.find_element_by_class_name("test-centre-results")
test_center = results_container.find_element_by_xpath(".//a")
test_center.click()
