import traceback

def SSandClose(b=None):
    if b:
        try:
            b.getScreenshot("failed situation")
            print b.role + " sceenshots saved in: " + b.screenshotPath
        except:
            print "error while making screenshot:"
            traceback.print_exc()
        try:
            b.close()
        except:
            print "error while closing browser:"
            traceback.print_exc()
