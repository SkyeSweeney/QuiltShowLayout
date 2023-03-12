# sample_one.py

import wx
import wx.grid


#---------------------------------------------------------------------------

class MyPageQuilts(wx.grid.Grid):
    def __init__(self, *args, **kw):
        super(MyPageQuilts, self).__init__(*args, **kw)

        self.SetLabelBackgroundColour('#DBD4D4')

        self.InitUI()
    #    

    def InitUI(self):

        nOfRows = 300
        nOfCols = 5

        self.row = self.col = 0
        self.CreateGrid(nOfRows, nOfCols)

        self.SetColLabelSize(40)
        self.SetRowLabelSize(80)

        self.SetColLabelValue(0, "ID")
        self.SetColLabelValue(1, "Class")
        self.SetColLabelValue(2, "Width")
        self.SetColLabelValue(3, "Height")
        self.SetColLabelValue(4, "Notes")

        # Load file
        self.LoadFile("Quilts.csv")

    #    


    def LoadFile(self, fn):

        fp = open(fn, "r")

        numRows = 0
        for line in fp:
            toks = line.split(",")
            numRows += 1
        #
        fp.close()

        # Resize the grid
        # TBD

        fp = open(fn, "r")

        self.BeginBatch()

        rowNo = 0
        for line in fp:
            toks = line.split(",")
            self.SetCellValue(rowNo,0, toks[0])   # Entry
            self.SetCellValue(rowNo,1, toks[1])   # Class
            self.SetCellValue(rowNo,2, toks[2])   # Width
            self.SetCellValue(rowNo,3, toks[3])   # Length
            self.SetCellValue(rowNo,4, toks[4])   # Notes
            rowNo += 1
        #
        fp.close()
        self.EndBatch()
        self.ForceRefresh()
    #

#---------------------------------------------------------------------------

class MyPageClasses(wx.grid.Grid):
    def __init__(self, *args, **kw):
        super(MyPageClasses, self).__init__(*args, **kw)

        self.SetLabelBackgroundColour('#DBD4D4')


        self.InitUI()

    def InitUI(self):
        nOfRows = 55
        nOfCols = 2

        self.row = self.col = 0
        self.CreateGrid(nOfRows, nOfCols)

        self.SetColLabelSize(20)
        self.SetRowLabelSize(20)

        self.SetColLabelValue(0, "Class")
        self.SetColLabelValue(1, "Notes")


#---------------------------------------------------------------------------
        
class MyPageRacks(wx.grid.Grid):
    def __init__(self, *args, **kw):
        super(MyPageRacks, self).__init__(*args, **kw)

        self.SetLabelBackgroundColour('#DBD4D4')


        self.InitUI()

    def InitUI(self):
        nOfRows = 55
        nOfCols = 14

        self.row = self.col = 0
        self.CreateGrid(nOfRows, nOfCols)

        self.SetColLabelSize(20)
        self.SetRowLabelSize(20)

        self.SetColLabelValue(0, "Row ID")
        self.SetColLabelValue(1, "Row")
        self.SetColLabelValue(2, "Side")
        self.SetColLabelValue(3, "Bay")
        self.SetColLabelValue(4, "Dxf Bay")
        self.SetColLabelValue(5, "Level")
        self.SetColLabelValue(6, "Slat Width")
        self.SetColLabelValue(7, "Act Width")
        self.SetColLabelValue(8, "Act Height")
        self.SetColLabelValue(9, "Left Pole")
        self.SetColLabelValue(10, "Right Pole")
        self.SetColLabelValue(11, "Class")
        self.SetColLabelValue(12, "Height Tol")
        self.SetColLabelValue(13, "Notes")


#---------------------------------------------------------------------------
        
class MyPageInventory(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        #------------
        
        #self.SetBackgroundColour(wx.Colour("Light Gray"))

        #------------
        
        txt = wx.StaticText(self, -1,
                            """This is a "Inventory" object""",
                            (60, 60))

#---------------------------------------------------------------------------
        
class MyPageErrors(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        #------------
        
        #self.SetBackgroundColour(wx.Colour("Light Gray"))

        #------------
        
        txt = wx.StaticText(self, -1,
                            """This is a "Errors" object""",
                            (60, 60))

#---------------------------------------------------------------------------
        
class MyPageLayout(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        #------------
        
        #self.SetBackgroundColour(wx.Colour("Light Gray"))

        #------------
        
        txt = wx.StaticText(self, -1,
                            """This is a "Layout" object""",
                            (60, 60))

#---------------------------------------------------------------------------
        
class MyPageOverrides(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        #------------
        
        #self.SetBackgroundColour(wx.Colour("Light Gray"))

        #------------
        
        txt = wx.StaticText(self, -1,
                            """This is a "Overrides" object""",
                            (60, 60))

#---------------------------------------------------------------------------
        
class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)

        self.SetIcon(wx.Icon('./wxwin.ico', wx.BITMAP_TYPE_ICO))
        
        #------------
        
        # Here we create a panel and a notebook on the panel.
        pnl = wx.Panel(self)
        nb = wx.Notebook(pnl)

        #------------
        
        # Create the page windows as children of the notebook.
        pageQuilts    = MyPageQuilts(nb)
        pageClasses   = MyPageClasses(nb)
        pageRacks     = MyPageRacks(nb)
        pageInventory = MyPageInventory(nb)
        pageErrors    = MyPageErrors(nb)
        pageLayout    = MyPageLayout(nb)
        pageOverrides = MyPageOverrides(nb)

        #------------
        
        # Add the pages to the notebook with the label to show on the tab.
        nb.AddPage(pageQuilts,    "Quilts")
        nb.AddPage(pageClasses,   "Classes")
        nb.AddPage(pageRacks,     "Racks")
        nb.AddPage(pageInventory, "Inventory")
        nb.AddPage(pageErrors,    "Errors")
        nb.AddPage(pageLayout,    "Layout")
        nb.AddPage(pageOverrides, "Overrides")

        #------------
        
        # Finally, put the notebook in a sizer for  
        # the panel to manage the layout.
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        pnl.SetSizer(sizer)

#---------------------------------------------------------------------------

class MyApp(wx.App):

    def OnInit(self):

        #------------

        self.frame = MyFrame(None, -1,
                        "Simple notebook example")
        self.SetTopWindow(self.frame)
        self.frame.Show(True)

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileItem = fileMenu.Append(wx.ID_EXIT, "Quit", "Quit Application")
        menubar.Append(fileMenu, '&File')
        self.frame.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)

        self.frame.SetSize((1200, 400))
        self.frame.SetTitle("Skye's Quilt Program")
        self.frame.Centre()

        return True

    def OnQuit(self, e):
        self.frame.Close()

#---------------------------------------------------------------------------

def main():
    app = MyApp(redirect=False)
    app.MainLoop()

#---------------------------------------------------------------------------

if __name__ == "__main__" :
    main()
