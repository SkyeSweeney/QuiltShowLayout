# sample_one.py

import wx
import wx.grid
import QuiltsClass
import ClassesClass
import RacksClass
import InventoryClass
import OverridesClass
import FileClass






#---------------------------------------------------------------------------

class MyApp(wx.App):

    ####################################################################
    #
    ####################################################################
    def OnInit(self):

        #------------

        self.frame = MyFrame(None, -1, "Hannah Dustin Quilt Guild Layout")
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
        quilts     = self.frame.pageQuilts.PullData()
        racks      = self.frame.pageRacks.PullData()
        orverrides = self.frame.pageOverrides.PullData()
        classes    = self.frame.pageClasses.PullData()
        fc = FileClass.FileClass()
        fc.write(self.fn, quilts, racks, overrides, classes, self.ini)
    #

    ####################################################################
    #
    ####################################################################
    def OnSaveas(self, e):

        fileDlg = wx.FileDialog(self.frame, 
                                "Open HDQG file", 
                                wildcard="HDQG files (*.hdqg)|*.hdqg",
                                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        ret = fileDlg.ShowModal()

        if (ret == wx.ID_CANCEL):
            return

        self.fn = fileDlg.GetPath()

        quilts     = self.frame.pageQuilts.PullData()
        racks      = self.frame.pageRacks.PullData()
        overrides  = self.frame.pageOverrides.PullData()
        classes    = self.frame.pageClasses.PullData()
        print("aaaa", classes)
        fc = FileClass.FileClass()
        fc.write(self.fn, quilts, racks, overrides, classes, self.ini)
        # TODO INI
    #

    ####################################################################
    #
    ####################################################################
    def OnOpen(self, e):

        fileDlg = wx.FileDialog(self.frame, 
                                "Open HDQG file", 
                                wildcard="HDQG files (*.hdqg)|*.hdqg",
                                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        ret = fileDlg.ShowModal()

        if (ret == wx.ID_CANCEL):
            return

        self.fn = fileDlg.GetPath()

        fc = FileClass.FileClass()
        (ret, quilts, racks, overrides, classes, self.ini) = fc.read(self.fn)
        self.frame.pageQuilts.LoadData(quilts)
        self.frame.pageRacks.LoadData(racks)
        self.frame.pageOverrides.LoadData(overrides)
        self.frame.pageClasses.LoadData(classes)
        # TODO INI
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
        
class MyFrame(wx.Frame):

    ####################################################################
    # Initialization routine
    ####################################################################
    def __init__(self, parent, id, title):

        # Call the default initialization routine
        wx.Frame.__init__(self, parent, id, title)

        self.SetIcon(wx.Icon('./wxwin.ico', wx.BITMAP_TYPE_ICO))
        
        #------------
        
        # Here we create a panel and a notebook on the panel.
        pnl = wx.Panel(self)
        nb = wx.Notebook(pnl)

        #------------
        
        # Create the page windows as children of the notebook.
        self.pageQuilts    = QuiltsClass.QuiltsClass(nb)
        self.pageClasses   = ClassesClass.ClassesClass(nb)
        self.pageRacks     = RacksClass.RacksClass(nb)
        self.pageOverrides = OverridesClass.OverridesClass(nb)
        self.pageInventory = InventoryClass.InventoryClass(nb)
        self.pageErrors    = MyPageErrors(nb)
        self.pageLayout    = MyPageLayout(nb)

        #------------
        
        # Add the pages to the notebook with the label to show on the tab.
        nb.AddPage(self.pageQuilts,    "Quilts")
        nb.AddPage(self.pageClasses,   "Classes")
        nb.AddPage(self.pageRacks,     "Racks")
        nb.AddPage(self.pageOverrides, "Overrides")
        nb.AddPage(self.pageInventory, "Inventory")
        nb.AddPage(self.pageErrors,    "Errors")
        nb.AddPage(self.pageLayout,    "Layout")

        #------------
        
        # Finally, put the notebook in a sizer for  
        # the panel to manage the layout.
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        pnl.SetSizer(sizer)
    #
#

# MOVE THESE TO THEIR OWN FILES
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

def main():
    app = MyApp(redirect=False)
    app.MainLoop()

#---------------------------------------------------------------------------

if __name__ == "__main__" :
    main()
