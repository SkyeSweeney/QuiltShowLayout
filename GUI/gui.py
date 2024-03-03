#! /usr/bin/python

########################################################################
#
# Program to aid in the setup of a quit show. It allocates quilt
# to hangind racks to minimize wasted space and maximize presentation.
#
#
########################################################################

import os

import wx
import wx.grid
import QuiltsClass
import ClassesClass
import RacksClass
import InventoryClass
import OverridesClass
import FileClass
import Storage
import Logger



# Main creates MyApp
# MyApp creates:
#       MyFrame
#       FileIf
#
# MyFrame creates
#       pageQuilts
#       pageClasses
#       pageRacks
#       pageOverrides
#       pageInventory
#       pageErrors
#       pageLayout    




#---------------------------------------------------------------------------

class MyApp(wx.App):

    ####################################################################
    #
    ####################################################################
    def OnInit(self):


        # Create the file interface
        FileIf = FileClass.FileClass()
        Storage.FileIf = FileIf


        Storage.Logger = Logger.Logger(self)
        Storage.Logger.SetDebug(True)

        self.frame = MyFrame(None, -1, "Hannah Dustin Quilt Guild Layout")
        self.SetTopWindow(self.frame)
        self.frame.Show(True)


        # Generate IDs we need
        self.ID_PLACE_QUILTS     = wx.Window.NewControlId()
        self.ID_GENERATE_DXF     = wx.Window.NewControlId()
        self.ID_IMPORT_QUILTS    = wx.Window.NewControlId()
        self.ID_IMPORT_RACKS     = wx.Window.NewControlId()
        self.ID_IMPORT_CLASSES   = wx.Window.NewControlId()
        self.ID_IMPORT_OVERRIDES = wx.Window.NewControlId()
        self.ID_EXPORT_QUILTS    = wx.Window.NewControlId()
        self.ID_EXPORT_RACKS     = wx.Window.NewControlId()
        self.ID_EXPORT_CLASSES   = wx.Window.NewControlId()
        self.ID_EXPORT_OVERRIDES = wx.Window.NewControlId()

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


        # Import menu
        importMenu = wx.Menu()
        importQuilts    = importMenu.Append(self.ID_IMPORT_QUILTS,    "Quilts",    "Import Quilts")
        importRacks     = importMenu.Append(self.ID_IMPORT_RACKS,     "Racks",     "Import Racks")
        importClasses   = importMenu.Append(self.ID_IMPORT_CLASSES,   "Classes",   "Import Classes")
        importOverrides = importMenu.Append(self.ID_IMPORT_OVERRIDES, "Overrides", "Import Overrides")
        menubar.Append(importMenu, '&Import')

        # Export menu
        exportMenu = wx.Menu()
        exportQuilts    = exportMenu.Append(self.ID_EXPORT_QUILTS,    "Quilts",    "Export Quilts")
        exportRacks     = exportMenu.Append(self.ID_EXPORT_RACKS,     "Racks",     "Export Racks")
        exportClasses   = exportMenu.Append(self.ID_EXPORT_CLASSES,   "Classes",   "Export Classes")
        exportOverrides = exportMenu.Append(self.ID_EXPORT_OVERRIDES, "Overrides", "Export Overrides")
        menubar.Append(exportMenu, '&Export')


        self.frame.SetMenuBar(menubar)


        # Bind menu events

        # File menu
        self.Bind(wx.EVT_MENU, self.OnQuit,   fileItemQuit)
        self.Bind(wx.EVT_MENU, self.OnSave,   fileItemSave)
        self.Bind(wx.EVT_MENU, self.OnSaveas, fileItemSaveas)
        self.Bind(wx.EVT_MENU, self.OnOpen,   fileItemOpen)

        # Action menu
        self.Bind(wx.EVT_MENU, self.OnPlace,  actionItemPlace)
        self.Bind(wx.EVT_MENU, self.OnDxf,    actionItemDxf)

        # Import menu
        self.Bind(wx.EVT_MENU, self.OnImportQuilts,    importQuilts)
        self.Bind(wx.EVT_MENU, self.OnImportRacks,     importRacks)
        self.Bind(wx.EVT_MENU, self.OnImportClasses,   importClasses)
        self.Bind(wx.EVT_MENU, self.OnImportOverrides, importOverrides)

        # Export menu
        self.Bind(wx.EVT_MENU, self.OnExportQuilts,    exportQuilts)
        self.Bind(wx.EVT_MENU, self.OnExportRacks,     exportRacks)
        self.Bind(wx.EVT_MENU, self.OnExportClasses,   exportClasses)
        self.Bind(wx.EVT_MENU, self.OnExportOverrides, exportOverrides)

        self.frame.SetSize((1200, 400))
        self.frame.Centre()

        return True

    ####################################################################
    #
    ####################################################################
    def OnImportQuilts(self, e):

        fileDlg = wx.FileDialog(self.frame, 
                                "Import Quilts CSV file", 
                                defaultDir=".",
                                defaultFile="quilts.csv",
                                wildcard="CSV files (*.csv)|*.csv",
                                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        ret = fileDlg.ShowModal()

        if (ret == wx.ID_CANCEL):
            return

        fn = fileDlg.GetPath()

        # Attempt to import the file
        fp = open(fn, "r")
        (ok, data) = Storage.QuiltsC.ImportFile(fp)
        fp.close()

        if ok:

            # Load the table
            Storage.QuiltsC.LoadData(data)
            Storage.QuiltsC.modified = False
            Storage.QuiltsC.loaded = True
        else:
            wx.MessageBox("Unable to read file", "Error",
                         wx.ICON_ERROR | wx.OK)
        #

    #

    ####################################################################
    #
    ####################################################################
    def OnImportRacks(self, e):

        fileDlg = wx.FileDialog(self.frame, 
                                "Import Racks CSV file", 
                                defaultDir=".",
                                defaultFile="racks.csv",
                                wildcard="CSV files (*.csv)|*.csv",
                                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        ret = fileDlg.ShowModal()

        if (ret == wx.ID_CANCEL):
            return

        fn = fileDlg.GetPath()

        # Attempt to import the file
        fp = open(fn, "r")
        (ok, data) = Storage.RacksC.ImportFile(fp)
        fp.close()

        if ok:

            # Load the table
            Storage.RacksC.LoadData(data)
            Storage.RacksC.modified = False
            Storage.RacksC.loaded = True
        else:
            wx.MessageBox("Unable to read file", "Error",
                         wx.ICON_ERROR | wx.OK)
        #

    #

    ####################################################################
    #
    ####################################################################
    def OnImportClasses(self, e):

        fileDlg = wx.FileDialog(self.frame, 
                                "Import Classes CSV file", 
                                defaultDir=".",
                                defaultFile="classes.csv",
                                wildcard="CSV files (*.csv)|*.csv",
                                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        ret = fileDlg.ShowModal()

        if (ret == wx.ID_CANCEL):
            return

        fn = fileDlg.GetPath()

        # Attempt to import the file
        fp = open(fn, "r")
        (ok, data) = Storage.ClassesC.ImportFile(fp)
        fp.close()

        if ok:

            # Load the table
            Storage.ClassesC.LoadData(data)
            Storage.ClassesC.modified = False
            Storage.ClassesC.loaded = True
        else:
            wx.MessageBox("Unable to read file", "Error",
                         wx.ICON_ERROR | wx.OK)
        #

    #

    ####################################################################
    #
    ####################################################################
    def OnImportOverrides(self, e):

        fileDlg = wx.FileDialog(self.frame, 
                                "Import Overrides CSV file", 
                                defaultDir=".",
                                defaultFile="overrides.csv",
                                wildcard="CSV files (*.csv)|*.csv",
                                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        ret = fileDlg.ShowModal()

        if (ret == wx.ID_CANCEL):
            return

        fn = fileDlg.GetPath()

        # Attempt to import the file
        fp = open(fn, "r")
        (ok, data) = Storage.OverridesC.ImportFile(fp)
        fp.close()

        if ok:

            # Load the table
            Storage.OverridesC.LoadData(data)
            Storage.OverridesC.modified = False
            Storage.OverridesC.loaded = True
        else:
            wx.MessageBox("Unable to read file", "Error",
                         wx.ICON_ERROR | wx.OK)
        #

        pass
    #

    ####################################################################
    #
    ####################################################################
    def OnExportQuilts(self, e):

        if Storage.FileIf.GetLoaded():

            fileDlg = wx.FileDialog(self.frame, 
                                    message="Export to CSV file", 
                                    defaultDir=".",
                                    defaultFile="quilts.csv",
                                    wildcard="CSV files (*.csv)|*.csv",
                                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            ret = fileDlg.ShowModal()

            if (ret == wx.ID_CANCEL):
                return

            # Get the supplied file name
            fn = fileDlg.GetPath()

            # Lets make sure it ends in csv
            split = os.path.splitext(fn)
            if (split[1] != ".csv"):
                fn = fn + ".csv"
            #    

            fp = open(fn, "w")
            quilts = Storage.QuiltsC.GetData()
            Storage.QuiltsC.ExportFile(fp, quilts)
            fp.close()

        else:
            wx.MessageBox("No file loaded to export", "Error",
                         wx.ICON_WARNING | wx.OK)
        #
    #

    ####################################################################
    #
    ####################################################################
    def OnExportRacks(self, e):

        if Storage.FileIf.GetLoaded():

            fileDlg = wx.FileDialog(self.frame, 
                                    message="Export to CSV file", 
                                    defaultDir=".",
                                    defaultFile="racks.csv",
                                    wildcard="CSV files (*.csv)|*.csv",
                                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            ret = fileDlg.ShowModal()

            if (ret == wx.ID_CANCEL):
                return

            # Get the supplied file name
            fn = fileDlg.GetPath()

            # Lets make sure it ends in csv
            split = os.path.splitext(fn)
            if (split[1] != ".csv"):
                fn = fn + ".csv"
            #    

            fp = open(fn, "w")
            classes = Storage.RacksC.GetData()
            Storage.RacksC.ExportFile(fp, classes)
            fp.close()

        else:
            wx.MessageBox("No file loaded to export", "Error",
                         wx.ICON_WARNING | wx.OK)
        #
    #

    ####################################################################
    #
    ####################################################################
    def OnExportClasses(self, e):

        if Storage.FileIf.GetLoaded():

            fileDlg = wx.FileDialog(self.frame, 
                                    message="Export to CSV file", 
                                    defaultDir=".",
                                    defaultFile="classes.csv",
                                    wildcard="CSV files (*.csv)|*.csv",
                                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            ret = fileDlg.ShowModal()

            if (ret == wx.ID_CANCEL):
                return

            # Get the supplied file name
            fn = fileDlg.GetPath()

            # Lets make sure it ends in csv
            split = os.path.splitext(fn)
            if (split[1] != ".csv"):
                fn = fn + ".csv"
            #    

            fp = open(fn, "w")
            classes = Storage.ClassesC.GetData()
            Storage.ClassesC.ExportFile(fp, classes)
            fp.close()

        else:
            wx.MessageBox("No file loaded to export", "Error",
                         wx.ICON_WARNING | wx.OK)
        #
    #

    ####################################################################
    #
    ####################################################################
    def OnExportOverrides(self, e):

        if Storage.FileIf.GetLoaded():

            fileDlg = wx.FileDialog(self.frame, 
                                    message="Export to CSV file", 
                                    defaultDir=".",
                                    defaultFile="overrides.csv",
                                    wildcard="CSV files (*.csv)|*.csv",
                                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            ret = fileDlg.ShowModal()

            if (ret == wx.ID_CANCEL):
                return

            # Get the supplied file name
            fn = fileDlg.GetPath()

            # Lets make sure it ends in csv
            split = os.path.splitext(fn)
            if (split[1] != ".csv"):
                fn = fn + ".csv"
            #    

            fp = open(fn, "w")
            quilts = Storage.OverridesC.GetData()
            Storage.OverridesC.ExportFile(fp, quilts)
            fp.close()

        else:
            wx.MessageBox("No file loaded to export", "Error",
                         wx.ICON_WARNING | wx.OK)
        #
    #

    ####################################################################
    #
    ####################################################################
    def OnQuit(self, e):

        # If the file loaded and modified?
        if Storage.FileIf.GetLoaded() and Storage.FileIf.GetAnyModified():
            wx.MessageBox("Project changed but not saved", "Error",
                          wx.ICON_WARNING | wx.OK)
            return
        else:
            self.frame.Close()
        #
    #

    ####################################################################
    # When a Save happens
    ####################################################################
    def OnSave(self, e):

        # If the file loaded and modified?
        if Storage.FileIf.GetLoaded():

            if Storage.FileIf.GetModified():
                quilts     = Storage.QuiltsC.PullData()
                racks      = Storage.RacksC.PullData()
                overrides  = Storage.OverridesC.PullData()
                classes    = Storage.ClassesC.PullData()
                fn = Storage.FileIf.GetFileName()
                ok = Storage.FileIf.write(fn, quilts, racks, overrides, classes, self.ini)
                if not ok:
                    wx.MessageBox("Unable to save file", "Error",
                                 wx.ICON_ERROR | wx.OK)
                else:
                    Storage.FileIf.SetAllModified(False)
                #    
            else:    
                wx.MessageBox("File not modified", "Error",
                             wx.ICON_WARNING | wx.OK)
            #
        else:
            wx.MessageBox("No file loaded", "Error",
                         wx.ICON_WARNING | wx.OK)
        #
    #

    ####################################################################
    # User requests a save as
    ####################################################################
    def OnSaveas(self, e):

        # If the file loaded
        if Storage.FileIf.GetLoaded():

            fileDlg = wx.FileDialog(self.frame, 
                                    "Open HDQG file", 
                                    wildcard="HDQG files (*.hdqg)|*.hdqg",
                                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            ret = fileDlg.ShowModal()

            if (ret == wx.ID_CANCEL):
                return

            # Get the supplied file name
            fn = fileDlg.GetPath()

            # Lets make sure it ends in HDQG
            split = os.path.splitext(fn)
            if (split[1] != "hdqg"):
                fn = fn + ".hdqg"

            quilts     = Storage.QuiltsC.PullData()
            racks      = Storage.RacksC.PullData()
            overrides  = Storage.OverridesC.PullData()
            classes    = Storage.ClassesC.PullData()
            ok = Storage.FileIf.write(fn, quilts, racks, overrides, classes, self.ini)

            if not ok:
                wx.MessageBox("Unable to save file", "Error",
                             wx.ICON_ERROR | wx.OK)
            else:
                Storage.FileIf.SetFileName(fn)
                Storage.FileIf.SetAllModified(False)
            #

        else:
            wx.MessageBox("No file loaded", "Error",
                         wx.ICON_WARNING | wx.OK)
        #

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

        fn = fileDlg.GetPath()

        (ret, quilts, racks, overrides, classes, self.ini) = Storage.FileIf.read(fn)
        if ret == True:
            Storage.QuiltsC.LoadData(quilts)
            Storage.RacksC.LoadData(racks)
            Storage.OverridesC.LoadData(overrides)
            Storage.ClassesC.LoadData(classes)
            # TODO INI
            Storage.FileIf.SetLoaded(True)
            Storage.FileIf.SetAllModified(False)
            Storage.FileIf.SetFileName(fn)
        else:
            wx.MessageBox("Unable to open file", "Error",
                         wx.ICON_ERROR | wx.OK)
        #


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

        #self.SetIcon(wx.Icon('./wxwin.ico', wx.BITMAP_TYPE_ICO))

        
        #------------
        
        # Here we create a panel and a notebook on the panel.
        pnl = wx.Panel(self)
        nb = wx.Notebook(pnl)

        #------------
        
        # Create the page windows as children of the notebook.
        Storage.QuiltsC    = QuiltsClass.QuiltsClass(nb)
        Storage.ClassesC   = ClassesClass.ClassesClass(nb)
        Storage.RacksC     = RacksClass.RacksClass(nb)
        Storage.OverridesC = OverridesClass.OverridesClass(nb)
        self.pageInventory = InventoryClass.InventoryClass(nb)
        self.pageErrors    = MyPageErrors(nb)
        self.pageLayout    = MyPageLayout(nb)

        #------------
        
        # Add the pages to the notebook with the label to show on the tab.
        nb.AddPage(Storage.QuiltsC,    "Quilts")
        nb.AddPage(Storage.ClassesC,   "Classes")
        nb.AddPage(Storage.RacksC,     "Racks")
        nb.AddPage(Storage.OverridesC, "Overrides")
        nb.AddPage(self.pageInventory, "Inventory")
        nb.AddPage(self.pageErrors,    "Errors")
        nb.AddPage(self.pageLayout,    "Layout")

        #------------
        
        # Finally, put the notebook in a sizer for  
        # the panel to manage the layout.
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        pnl.SetSizer(sizer)


        Storage.statusbar = self.CreateStatusBar(2)
        Storage.statusbar.SetStatusText("No file loaded", 0)
        Storage.statusbar.SetStatusText("aaaa", 1)
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
