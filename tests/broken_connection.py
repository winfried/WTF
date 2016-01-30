import time
import traceback

import settings
import sites
from util import SSandClose

s=None
c=None
def test(config):
    try:
        s = sites.sites['serviant'].StaffBrowser(settings.browsers[config['staff_browser']])
        s.login()
        c = sites.sites['serviant'].ClientBrowser(settings.browsers[config['client_browser']])
        c.openChat()
        s.waitForClient()
        for n in range(2):
            c.waitForChatLine(s.sendChatLine())
            s.waitForChatLine(c.sendChatLine())
        if config['client_disconnect'] == 'DROP':
            c.dropTraffic()
        elif config['client_disconnect'] == 'REJECT':
            c.rejectTraffic()
        if config['staff_disconnect'] == 'DROP':
            s.dropTraffic()
        elif config['staff_disconnect'] == 'REJECT':
            s.rejectTraffic()
        time.sleep(config['disconnect_time']/2)
        clientLastLine = None
        if config['client_send_during_disconnect']:
            clientLastLine = c.sendChatLine()
        staffLastLine = None
        if config['staff_send_during_disconnect']:
            staffLastLine = s.sendChatLine()
        time.sleep(config['disconnect_time']/2)
        #debug
        time.sleep(600)
        if config['client_disconnect']:
            c.acceptTraffic()
        if config['staff_disconnect']:
            s.acceptTraffic()
        time.sleep(config['reconnect_time'])
        if clientLastLine:
            s.waitForChatLine(clientLastLine)
        if staffLastLine:
            c.waitForChatLine(staffLastLine)
        for n in range(2):
            c.waitForChatLine(s.sendChatLine())
            s.waitForChatLine(c.sendChatLine())
        if config['staff_initiates_close']:
            s.closeChat()
            c.confirmClose()
        else:
            c.closeChat()
        s.close()
        c.close()
        print "-> succes!"
    except:
        print "-> failed!"
        traceback.print_exc()
        if c:
            if config['client_disconnect']:
                c.acceptTraffic()
            SSandClose(c)
        if s:
            if config['staff_disconnect']:
                s.acceptTraffic()
            SSandClose(s)
        next
