#!/usr/bin/python
# -*- coding: utf-8 -*-
# needs python selenium bindings, unfortunately available in Debian
# use: sudo easy_install install selenium or sudo pip install selenium
#
# tests can be run individually by using:
# > python browser_test.py
# and then run tests one by one:
# >>> test_closed()
# or by running the tests with py.test (pytest package)

import os
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# some global counters and constants
browserInstanceCount = 0
screenshotCount = 0
screenshotPath = '/tmp' # ToDo: make something better
screenshotSubDir = time.strftime("%Y-%m-%d_%H%M%S")
timeout = 5 # global default for timeout in 'waitfor'

class BrowserBase:
    """Baseclass for a browser to use for testing"""
    def __init__(self, localBrowserId=None, remoteBrowserDefinition=None,
                 name="", firefoxPlugins=False):
        #setup the driver and the id
        self.driver = None
        if localBrowserId: 
            if localBrowserId == "Chrome":
                # note the chromedriver is not in a correct path in Debian,
                # make a symlink to /usr/lib/chromium/chromedriver
                self.driver = webdriver.Chrome()
            elif localBrowserId == "Firefox":
                if firefoxPlugins:
                    profile = webdriver.FirefoxProfile()
                    for fle in os.listdir("."):
                        if fle.endswith(".xpi"):
                            profile.add_extension(extension=fle)
                            #Avoid startup screen
                            flesplit = fle.split("-")
                            if flesplit[0] == "firebug":
                                profile.set_preference("extensions.firebug.currentVersion", flesplit[1])
                    self.driver = webdriver.Firefox(firefox_profile=profile)
                else:
                    self.driver = webdriver.Firefox()
            elif localBrowserId == "IE":
                self.driver = webdriver.IE()
            elif localBrowserId == "Opera":
                self.driver = webdriver.Opera()
            elif localBrowserId == "Safari":
                self.driver = webdriver.Safari()
            else:
                raise Exception("Unknown localBrowserId")
            self.browserId = localBrowserId
        elif remoteBrowserDefinition:
            # should be a dict with 'caps' and 'executor'
            # caps should have format:
            # (webdriver.DesiredCapabilities.XXX,
            #     {'aditional_key': 'aditional_value'}
            caps = remoteBrowserDefinition['caps'][0].copy()
            for capsAttName in remoteBrowserDefinition['caps'][1].keys():
                caps[capsAttName] = remoteBrowserDefinition['caps'][1][capsAttName]
            capsname = ''
            for item in caps.keys():
                if capsname:
                    capsname += ' | '
                capsname += str(caps[item])
            caps["name"] = capsname
            self.driver = webdriver.Remote(
                remoteBrowserDefinition['executor'],
                caps)
            self.browserId = capsname
        else:
            raise Exception("Need a local or a remote browser definition")
        #setup everything else needed
        if name:
            self.name = name
        else:
            self.name = self.browserId
        #make this global: we want this to add up
        global browserInstanceCount
        browserInstanceCount += 1
        self.instance = browserInstanceCount + 0 #deep copy
        self.lineCount = 0
        self.screenshotPath = os.path.abspath(
            os.path.join(screenshotPath, screenshotSubDir))
        if not os.path.isdir(self.screenshotPath):
            os.makedirs(self.screenshotPath)
        self.role = "unknown" # override this with 'staff' or 'client'
        return

    def getScreenshot(self, description):
        global screenshotCount
        screenshotCount += 1
        filename = "".join((str(screenshotCount), "_",
                            self.browserId, "_",
                            str(self.instance), "_",
                            self.role, "_",
                            description, ".png"))
        fullpath = os.path.join(self.screenshotPath, filename)
        self.driver.get_screenshot_as_file(fullpath)

    def close(self):
        self.driver.quit()

    # utility methods to make programming a bit easier
    def waitFor(self, by, search, text=None, timeout=timeout):
        # fail with exception, should be caught by testframework
        if text:
            WebDriverWait(self.driver, timeout).until(
                EC.text_to_be_present_in_element((by, search), text))
        else:                
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, search)))

    def waitForXPath(self, XPath, text=None, timeout=timeout):
        self.waitFor(By.XPATH, XPath, text, timeout)

    def waitForID(self, ID, text=None, timeout=timeout):
        self.waitFor(By.ID, ID, text, timeout)

    def waitForTag(self, Tag, text=None, timeout=timeout):
        self.waitFor(By.TAG_NAME, Tag, text, timeout)

    def waitForClass(self, Class, text=None, timeout=timeout):
        self.waitFor(By.CLASS_NAME, Class, text, timeout)

    def waitForName(self, Name, text=None, timeout=timeout):
        self.waitFor(By.NAME, Name, text)

    def waitForSelector(self, Selector, text=None, timeout=timeout):
        self.waitFor(By.CSS_SELECTOR, Selector, text, timeout)

    def waitForTitle(self, title, timeout=timeout):
        WebDriverWait(self.driver, timeout).until(
            EC.title_is(title))

    # methods to be subclassed
    def openChat(self, slowDown=0):
        """All steps needed to setup a chat, adds 'slowDown' seconds between
           *every step* to simulate slow user interaction"""
        # to be subclassed
        pass

    def closeChat(self, slowDown=0):
        """All steps needed to close the active chat, adds 'slowDown'
           seconds between *every step* to simulate slow user interaction"""
        # to be subclassed
        pass

    def waitForChatLine(self, line, timeout=timeout):
        "Waits for 'line' to appear in the chat"
        # to be subclassed
        pass

    def sendChatLine(self, line = None, send=True):
        "Sends 'line' to the chat"
        # to be subclassed
        pass

    def getLastChatLine(self, delay=0):
        "returns the last Chatline, waits 'delay' seconds before retrieving"
        time.sleep(delay)
        # to be subclassed
        pass

    def peerIsTyping(self):
        "Returns 'true' if the browser shows a 'composing' message for the peer"
        # to be subclassed
        pass

    def peerStoppedTyping(self):
        "Returns 'true' if the browser shows a 'stopped composing' message for the peer"
        # to be subclassed
        pass
