
class Logger:

    def __init__(self):
        self.win = None
        self.debug = False
    #

    def SetWindow(self, win):
        self.win = win
    #    

    def SetDebug(self, b):
        self.debug = b
    #    

    def LogError(self, error):
        if self.win == None:
            print("ERR: %s" % error)
        else:
            pass
        #
    #
    
    def LogWarning(self, warning):
        if self.win == None:
            print("WRN: %s" % warning)
        else:
            pass
        #
    #

    def LogNotice(self, notice):
        if self.win == None:
            print("NTC: %s" % notice)
        else:
            pass
        #
     #

    def LogDebug(self, debug):
        if self.debug:
            if self.win == None:
                print("DBG: %s" % debug)
            else:
                pass
            #
         #
     #
#
