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
import subprocess
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
timeout = 30 # global default for timeout in 'waitfor'

class BrowserBase:
    """Baseclass for a browser to use for testing"""
    def __init__(self, browserId, name="", firefoxPlugins=False):
        #setup the driver and the id
        self.driver = None
        if type(browserId) == str:
            if browserId == "Chrome":
                # note the chromedriver is not in a correct path in Debian,
                # make a symlink to /usr/lib/chromium/chromedriver
                self.driver = webdriver.Chrome()
            elif browserId == "Firefox":
                if firefoxPlugins:
                    for fle in firefoxPlugins:
                        profile.add_extension(extension=fle)
                        #Avoid firebug startup screen
                        if "firebug" in fle:
                            profile.set_preference("extensions.firebug.currentVersion", flesplit[1])
                    self.driver = webdriver.Firefox(firefox_profile=profile)
                else:
                    self.driver = webdriver.Firefox()
            elif browserId == "IE":
                self.driver = webdriver.IE()
            elif browserId == "Opera":
                self.driver = webdriver.Opera()
            elif browserId == "Safari":
                self.driver = webdriver.Safari()
            else:
                raise Exception("Unknown localBrowserId")
            self.browserId = browserId
            self.local = True
        elif type(browserId) == dict:
            # should be a dict with 'caps' and 'executor'
            # caps should have format:
            # {'browserName': "internet explorer",
            #  'platform':    "Windows 7",
            #  'version':     "10.0",
            #  'aditional_key': 'aditional_value'}
            caps = browserId['caps']
            # create a nice name
            capsname =  caps.get('platform', "platform?") + " | " + caps.get('browserName', "name?") + " " + caps.get('version', "v?") + " | " + self.role
            caps["name"] = capsname
            self.driver = webdriver.Remote(
                command_executor = browserId['executor'],
                desired_capabilities = caps)
            self.browserId = capsname
            self.local = False
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
        self.sendChatLineXPath = None # override this with the xpath to the chat send line
        self.activeIptablesRules = []
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
    def waitFor(self, by, search, text=None, timeout=timeout, clickable=False):
        # fail with exception, should be caught by testframework
        if text:
            WebDriverWait(self.driver, timeout).until(
                EC.text_to_be_present_in_element((by, search), text))
        elif clickable:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, search)))
        else:                
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, search)))

    def waitForXPath(self, XPath, text=None, timeout=timeout, clickable=False):
        self.waitFor(By.XPATH, XPath, text, timeout, clickable)

    def waitForID(self, ID, text=None, timeout=timeout, clickable=False):
        self.waitFor(By.ID, ID, text, timeout, clickable)

    def waitForTag(self, Tag, text=None, timeout=timeout, clickable=False):
        self.waitFor(By.TAG_NAME, Tag, text, timeout, clickable)

    def waitForClass(self, Class, text=None, timeout=timeout, clickable=False):
        self.waitFor(By.CLASS_NAME, Class, text, timeout, clickable)

    def waitForName(self, Name, text=None, timeout=timeout, clickable=False):
        self.waitFor(By.NAME, Name, text, clickable)

    def waitForSelector(self, Selector, text=None, timeout=timeout, clickable=False):
        self.waitFor(By.CSS_SELECTOR, Selector, text, timeout, clickable)

    def waitForTitle(self, title, timeout=timeout):
        WebDriverWait(self.driver, timeout).until(
            EC.title_is(title))

    def sendChatLine(self, line = None, send=True):
        if not line:
            self.lineCount += 1
            line = "I am %s, using a %s browser (instance %d) and sending line: %d" %(
                self.role,
                self.browserId,
                self.instance,
                self.lineCount)
        self.waitForXPath(self.sendChatLineXPath, clickable=True)
        #print "xpath clickable"
        self.driver.find_element_by_xpath(self.sendChatLineXPath).click()
        #print "clicked"
        self.driver.find_element_by_xpath(self.sendChatLineXPath).send_keys(line)
        #print "text typed"
        if send:
            self.driver.find_element_by_xpath(self.sendChatLineXPath).send_keys(Keys.ENTER)
            #print "pressed ENTER"
        return line

    def dropTraffic(self):
        """Add an iptables rule to drop traffic to chatserver
            Needs in /etc/sudoers:
            username ALL=(ALL) NOPASSWD: /sbin/iptables"""
        print "droppping traffic ..."
        # todo add ipv6 support!
        if not self.local:
            raise Exception("can only filter local traffic")
        iptDef = "OUTPUT -d {} -p tcp --dport {:d} -j DROP".format(self.settings['blockHosts'], self.settings['blockPorts'])
        if subprocess.call(["sudo", "iptables", "-I"]+iptDef.split()):
            raise Exception("Call to iptables failed: "+iptDef)
        self.activeIptablesRules.append(iptDef)
        iptDef = "INPUT -s {} -p tcp --sport {:d} -j DROP".format(self.settings['blockHosts'], self.settings['blockPorts'])
        if subprocess.call(["sudo", "iptables", "-I"]+iptDef.split()):
            raise Exception("Call to iptables failed: "+iptDef)
        self.activeIptablesRules.append(iptDef)

    def rejectTraffic(self):
        """Add an iptables rule to reject traffic to chatserver
            Needs in /etc/sudoers:
            username ALL=(ALL) NOPASSWD: /sbin/iptables"""
        print "rejectinging traffic ..."
        # todo add ipv6 support!
        if not self.local:
            raise Exception("can only filter local traffic")
        iptDef = "OUTPUT -d {} -p tcp --dport {:d} -j REJECT".format(self.settings['blockHosts'], self.settings['blockPorts'])
        if subprocess.call(["sudo", "iptables", "-I"]+iptDef.split()):
            raise Exception("Call to iptables failed: "+iptDef)
        self.activeIptablesRules.append(iptDef)
        iptDef = "INPUT -s {} -p tcp --sport {:d} -j REJECT".format(self.settings['blockHosts'], self.settings['blockPorts'])
        if subprocess.call(["sudo", "iptables", "-I"]+iptDef.split()):
            raise Exception("Call to iptables failed: "+iptDef)
        self.activeIptablesRules.append(iptDef)

    def acceptTraffic(self):
        """Clear all added iptables rules
            Needs in /etc/sudoers:
            username ALL=(ALL) NOPASSWD: /sbin/iptables"""
        print "... accepting traffic ..."
        # todo add ipv6 support!
        if not self.local:
            raise Exception("can only filter local traffic")
        for iptDef in self.activeIptablesRules:
            if subprocess.call(["sudo", "iptables", "-D"]+iptDef.split()):
                raise Exception("Call to iptables failed: "+iptDef)
        self.activeIptablesRules = []

    # methods to be subclassed
    def openChat(self, slowDown=0):
        """All steps needed to setup a chat, adds 'slowDown' seconds between
           *every step* to simulate slow user interaction. Note for staff,
           usually this has to be split up to 'login' and 'waitForClient:
           many systems only allow a client to enter when a staff is logged in."""
        # to be subclassed
        pass

    def login(self, slowDown=0):
        """All steps needed to login as Staff."""
        # to be subclassed
        pass

    def waitForClient(self, slowDown=0):
        """Wait for client to request a chat and accept it (if applicable).
           Note: blocking!"""
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

    def reloadWhenRequested(self):
        """Looks if there is a request (popup?) that asks for a reload, reload"""
        # to be subclassed if applicable
        pass
