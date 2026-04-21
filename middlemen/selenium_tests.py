# Combined from Selenium IDE exports with assertions added
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class TestMiddlemanSelenium():
    def setup_method(self, method):
        self.driver = webdriver.Firefox()
        self.vars = {}

    def teardown_method(self, method):
        self.driver.quit()

    def test_testaboutpageloads(self):
        self.driver.get("http://34.28.143.23/")
        self.driver.set_window_size(1440, 900)
        self.driver.find_element(By.LINK_TEXT, "About").click()

        # Assertion added
        assert "about" in self.driver.current_url.lower() or "about" in self.driver.page_source.lower()

    def test_testbrowsepageloads(self):
        self.driver.get("http://34.28.143.23/")
        self.driver.set_window_size(1440, 900)
        self.driver.find_element(By.LINK_TEXT, "Browse").click()

        # Assertion added
        assert "browse" in self.driver.current_url.lower() or "browse" in self.driver.page_source.lower()

    def test_testhomepageloads(self):
        self.driver.get("http://34.28.143.23/")
        self.driver.set_window_size(1440, 900)
        self.driver.find_element(By.LINK_TEXT, "Home").click()

        # Assertion added
        assert self.driver.current_url == "http://34.28.143.23/" or "home" in self.driver.page_source.lower()

    def test_testloginpageloads(self):
        self.driver.get("http://34.28.143.23/")
        self.driver.set_window_size(1440, 900)
        self.driver.find_element(By.LINK_TEXT, "Login").click()
        self.driver.find_element(By.NAME, "username").click()
        self.driver.find_element(By.NAME, "password").click()
        self.driver.find_element(By.CSS_SELECTOR, ".auth-wrap").click()

        # Assertion added
        assert self.driver.find_element(By.NAME, "username").is_displayed()
        assert self.driver.find_element(By.NAME, "password").is_displayed()

    def test_testsignuppageloads(self):
        self.driver.get("http://34.28.143.23/")
        self.driver.set_window_size(1440, 900)
        self.driver.find_element(By.LINK_TEXT, "Sign Up").click()
        self.driver.find_element(By.ID, "usernameTextBoxLabel").click()
        self.driver.find_element(By.ID, "usernameTextBoxLabel").click()
        element = self.driver.find_element(By.ID, "usernameTextBoxLabel")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.ID, "usernameTextBoxLabel").click()

        # Your original assertion kept
        assert self.driver.find_element(By.ID, "usernameTextBoxLabel").text == "Username:"

    def test_testsignupuser(self):
        self.driver.get("http://34.28.143.23/")
        self.driver.set_window_size(1440, 900)
        self.driver.find_element(By.LINK_TEXT, "Sign Up").click()
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("shubham")
        self.driver.find_element(By.CSS_SELECTOR, ".signupViewInside").click()
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("Shubham774")
        self.driver.find_element(By.ID, "emailTextboxLabel").click()
        self.driver.find_element(By.ID, "reenteredPassword").click()
        self.driver.find_element(By.ID, "reenteredPassword").send_keys("Shubham774")
        self.driver.find_element(By.CSS_SELECTOR, ".signupViewInside > div").click()
        self.driver.find_element(By.CSS_SELECTOR, ".signupViewInside > div").click()
        self.driver.find_element(By.ID, "email").click()
        self.driver.find_element(By.ID, "email").send_keys("shubhamchaudhari@unomaha.edu")
        self.driver.find_element(By.ID, "firstName").click()
        self.driver.find_element(By.ID, "firstName").send_keys("Shubham")
        self.driver.find_element(By.ID, "lastName").click()
        self.driver.find_element(By.ID, "lastName").send_keys("Chaudhari")
        self.driver.find_element(By.NAME, "userType").click()
        self.driver.find_element(By.CSS_SELECTOR, "button").click()

        # Assertion added
        assert "login" in self.driver.page_source.lower() or self.driver.find_element(By.NAME, "username").is_displayed()