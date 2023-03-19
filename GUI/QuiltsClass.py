
import wx
import wx.grid
import Storage


#---------------------------------------------------------------------------

class QuiltsClass(wx.grid.Grid):

    ####################################################################
    # Constructor
    ####################################################################
    def __init__(self, *args, **kw):

        super(QuiltsClass, self).__init__(*args, **kw)

        self.SetLabelBackgroundColour('#DBD4D4')

        self.loaded = False
        self.modified = False

        self.InitUI()

    #    


    ####################################################################
    # Init the UI
    ####################################################################
    def InitUI(self):

        self.CreateGrid(1, 5)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED,      self.OnCellChanged)
        self.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK,  self.OnRightDown)

        self.SetColLabelSize(40)
        self.SetRowLabelSize(80)

        self.SetColLabelValue(0, "ID")
        self.SetColLabelValue(1, "Class")
        self.SetColLabelValue(2, "Width")
        self.SetColLabelValue(3, "Height")
        self.SetColLabelValue(4, "Notes")

        
        self.data = []

        # Load file
        self.LoadData(self.data)
    #




    ####################################################################
    # Called when cell changes value
    ####################################################################
    def OnCellChanged(self, event):

        row = event.GetRow()
        col = event.GetCol()
        was = event.GetString() # Original value
        now = self.GetCellValue(row, col) # New value
        Storage.Logger.LogDebug("Changed %d %d <%s> -> <%s>" % (row, col, was, now))

        # Check the validity of the change

        # Mark file as changed
        self.modified = True
        Storage.FileIf.SetModified(True)

    #

    ####################################################################
    # Right click on row labels
    ####################################################################
    def OnLabelRightClick(self, event):
        row = event.GetRow()

        self.InsertRows(row, 1)
        Storage.QuiltsC.modified = True
    #


    ####################################################################
    # Right click on a cell
    ####################################################################
    def OnRightDown(self, event):

        # Bring up context menu and get selection
        menu = ContextMenu("TTTTT")
        self.PopupMenu(menu, event.GetPosition())
        selection = menu.GetSelection()
        menu.Destroy()

        # Get the selected row
        row = event.GetRow()

        # No selection
        if selection == 0:
            pass

        # Insert row above
        elif selection == 1:
            self.InsertRows(row, 1)
            Storage.QuiltsC.modified = True

        # Insert row bellow
        elif selection == 2:
            self.InsertRows(row+1, 1)
            Storage.QuiltsC.modified = True

        # Delete Row
        elif selection == 3:
            self.DeleteRows(row, 1)
            Storage.QuiltsC.modified = True

        # Undefines    
        else:
            Storage.Logger.LogError("Bad case number")
        #    
    #


    ####################################################################
    # Load the table from a list of lines
    ####################################################################
    def LoadData(self, data):


        self.BeginBatch()
            
        # Nuke the current grid
        if self.GetNumberRows() != 0:
            self.DeleteRows(0, self.GetNumberRows())
        #    

        # Size for the new grid
        self.InsertRows(0, len(data))

        rowNo = 0
        for toks in data:
            self.SetCellValue(rowNo,0, toks[0])   # Entry
            self.SetCellValue(rowNo,1, toks[1])   # Class
            self.SetCellValue(rowNo,2, toks[2])   # Width
            self.SetCellValue(rowNo,3, toks[3])   # Length
            self.SetCellValue(rowNo,4, toks[4])   # Notes
            self.data.append(toks)
            rowNo += 1
        #
        self.EndBatch()
        self.ForceRefresh()
    #

    ####################################################################
    # Pull data from table
    ####################################################################
    def PullData(self):

        data = []
        toks = [0] * 5

        rows = self.GetNumberRows()

        for iRow in range(rows):
            toks[0] = self.GetCellValue(iRow, 0)   # Entry
            toks[1] = self.GetCellValue(iRow, 1)   # Class
            toks[2] = self.GetCellValue(iRow, 2)   # Width
            toks[3] = self.GetCellValue(iRow, 3)   # Lenght
            toks[4] = self.GetCellValue(iRow, 4)   # Notes
            data.append(list(toks))
        #
        return data
    #



    ####################################################################
    # Get loaded data
    ####################################################################
    def GetData(self):
        return self.data
    #

    ####################################################################
    # Read the section from the HDQG file
    # Does not update the loaded data set
    ####################################################################
    def ImportFile(self, fp):

        data = []

        # Read the Column header line
        line = fp.readline().strip()

        if ("QID,Class,Width,Length,Notes" not in line):
            Storage.Logger.LogError("Missing Quilt column header")
            return (False, data)
        #

        # Read lines till we find the #END token or EOF
        while True:

            # Get next line
            line = fp.readline().strip()

            # End if the END token or EOF
            if (line == "#END") or (line == ""):
                break
            #

            # Split into tokens
            toks = line.split(",")

            # Insure we have 5
            if (len(toks) != 5):
                Storage.Logger.LogError("Invalid number of columns in Quilts")
                return (False, [])
            else:
                data.append(toks)
            #
        #    

        return (True, data)

    #

    ####################################################################
    # Export the data to a CSV file
    # Does not update the loaded data set
    # Does not write the #CLASSES or #END tokens
    # Leaves the file open
    ####################################################################
    def ExportFile(self, fp, data):

        # Write header
        fp.write("QID,Class,Width,Length,Notes\n")

        # Write data
        for toks in data:
            s = "%s,%s,%s,%s,%s\n" % \
            (toks[0],
            toks[1],
            toks[2],
            toks[3],
            toks[4])
            fp.write(s)
        #

    #

#    

class ContextMenu(wx.Menu):

    def __init__(self, WinName):
        wx.Menu.__init__(self)

        self.WinName = WinName
        self.selection = 0

        # menu item 1
        item = wx.MenuItem(self, wx.NewId(), 'Insert Row Above ')
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.OnInsertAbove, item)

        # menu item 2
        item = wx.MenuItem(self, wx.NewId(), 'Insert Row Bellow')
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.OnInsertBellow, item)

        # menu item 2
        item = wx.MenuItem(self, wx.NewId(), 'Delete Row')
        self.Append(item)
        self.Bind(wx.EVT_MENU, self.OnDeleteRow, item)

    def GetSelection(self):
        return self.selection

    def OnInsertAbove(self, event):
        self.selection = 1

    def OnInsertBellow(self, event):
        self.selection = 2

    def OnDeleteRow(self, event):
        self.selection = 3
