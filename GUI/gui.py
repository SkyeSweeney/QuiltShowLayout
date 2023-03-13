# sample_one.py

import wx
import wx.grid
import QuiltsClass
import ClassesClass
import RacksClass
import InventoryClass
import OverridesClass




#---------------------------------------------------------------------------
        
class MyPageErrors(wx.Panel):

    ####################################################################
    #
    ####################################################################
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        
        txt = wx.StaticText(self, -1,
                            """This is a "Errors" object""",
                            (60, 60))

#---------------------------------------------------------------------------
        
class MyPageLayout(wx.Panel):

    ####################################################################
    #
    ####################################################################
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        
        txt = wx.StaticText(self, -1,
                            """This is a "Layout" object""",
                            (60, 60))


#---------------------------------------------------------------------------
        
class MyFrame(wx.Frame):

    ####################################################################
    #
    ####################################################################
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)

        self.SetIcon(wx.Icon('./wxwin.ico', wx.BITMAP_TYPE_ICO))
        
        #------------
        
        # Here we create a panel and a notebook on the panel.
        pnl = wx.Panel(self)
        nb = wx.Notebook(pnl)

        #------------
        
        # Create the page windows as children of the notebook.
        pageQuilts    = QuiltsClass.QuiltsClass(nb)
        pageClasses   = ClassesClass.ClassesClass(nb)
        pageRacks     = RacksClass.RacksClass(nb)
        pageOverrides = OverridesClass.OverridesClass(nb)
        pageInventory = InventoryClass.InventoryClass(nb)
        pageErrors    = MyPageErrors(nb)
        pageLayout    = MyPageLayout(nb)

        #------------
        
        # Add the pages to the notebook with the label to show on the tab.
        nb.AddPage(pageQuilts,    "Quilts")
        nb.AddPage(pageClasses,   "Classes")
        nb.AddPage(pageRacks,     "Racks")
        nb.AddPage(pageOverrides, "Overrides")
        nb.AddPage(pageInventory, "Inventory")
        nb.AddPage(pageErrors,    "Errors")
        nb.AddPage(pageLayout,    "Layout")

        #------------
        
        # Finally, put the notebook in a sizer for  
        # the panel to manage the layout.
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        pnl.SetSizer(sizer)

#---------------------------------------------------------------------------

class MyApp(wx.App):

    ####################################################################
    #
    ####################################################################
    def OnInit(self):

        #------------

        self.frame = MyFrame(None, -1,
                        "Simple notebook example")
        self.SetTopWindow(self.frame)
        self.frame.Show(True)


        # Generate IDs we need
        self.ID_PLACE_QUILTS = wx.Window.NewControlId()
        self.ID_GENERATE_DXF = wx.Window.NewControlId()

        #---------------------------
        # Create menu
        #---------------------------

        # Main menu object
        menubar = wx.MenuBar()

        # FILE menu
        fileMenu = wx.Menu()
        fileItemOpen   = fileMenu.Append(wx.ID_OPEN,   "Open",     "Open a project")
        fileItemSave   = fileMenu.Append(wx.ID_SAVE,   "Save",    "Save project")
        fileItemSaveas = fileMenu.Append(wx.ID_SAVEAS, "Save as", "Save project as")
        fileItemQuit   = fileMenu.Append(wx.ID_EXIT,   "Quit",    "Quit Application")
        menubar.Append(fileMenu, '&File')


        # Action menu
        actionMenu = wx.Menu()
        actionItemPlace = actionMenu.Append(self.ID_PLACE_QUILTS,  "Place Quilts",   "Place quilts")
        actionItemDxf   = actionMenu.Append(self.ID_GENERATE_DXF,  "Generate DXF",   "Generate DXF files")
        menubar.Append(actionMenu, '&Action')

        self.frame.SetMenuBar(menubar)



        # Bind menu events
        self.Bind(wx.EVT_MENU, self.OnQuit,   fileItemQuit)
        self.Bind(wx.EVT_MENU, self.OnSave,   fileItemSave)
        self.Bind(wx.EVT_MENU, self.OnSaveas, fileItemSaveas)
        self.Bind(wx.EVT_MENU, self.OnOpen,   fileItemOpen)

        self.Bind(wx.EVT_MENU, self.OnPlace, actionItemPlace)
        self.Bind(wx.EVT_MENU, self.OnDxf,   actionItemDxf)

        self.frame.SetSize((1200, 400))
        self.frame.SetTitle("Skye's Quilt Program")
        self.frame.Centre()

        return True

    ####################################################################
    #
    ####################################################################
    def OnQuit(self, e):
        self.frame.Close()
    #

    ####################################################################
    #
    ####################################################################
    def OnSave(self, e):
        print("Save")
    #

    ####################################################################
    #
    ####################################################################
    def OnSaveas(self, e):
        print("Saveas")
    #

    ####################################################################
    #
    ####################################################################
    def OnOpen(self, e):
        print("Open")
    #

    ####################################################################
    #
    ####################################################################
    def OnPlace(self, e):
        print("Place quilts")
    #

    ####################################################################
    #
    ####################################################################
    def OnDxf(self, e):
        print("Generating DXF")
    #
#

#---------------------------------------------------------------------------

def main():
    app = MyApp(redirect=False)
    app.MainLoop()

#---------------------------------------------------------------------------

if __name__ == "__main__" :
    main()
