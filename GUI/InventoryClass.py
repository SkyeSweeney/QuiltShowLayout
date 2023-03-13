
import wx

        
class InventoryClass(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        txt = wx.StaticText(self, -1,
                            """This is a "Inventory" object""",
                            (60, 60))
    #
#
