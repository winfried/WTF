#!/usr/bin/env python

import time
import sites

browsers = ['Firefox']
browsers = ['Chrome']
browsers = ['Chrome', 'Firefox']

for browser in browsers:
    b = sites.serviant.StaffBrowser(browser)
    b.openChat()
    time.sleep(10)
    b.close()
