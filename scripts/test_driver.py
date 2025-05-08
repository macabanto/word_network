from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://www.google.com")
# print(driver.title)  # Should print "Google"
driver.quit()