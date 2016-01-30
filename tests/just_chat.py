import settings
import traceback

import sites
from util import SSandClose


def test(config):
    try:
        s = sites.sites['serviant'].StaffBrowser(settings.browsers[config['staff_browser']])
        s.login()
        c = sites.sites['serviant'].ClientBrowser(settings.browsers[config['client_browser']])
        c.openChat()
        s.waitForClient()
        for n in range(3):
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
        SSandClose(c)
        SSandClose(s)
