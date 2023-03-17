
import wx
import wx.grid
import Storage


#---------------------------------------------------------------------------

class ClassesClass(wx.grid.Grid):

    ####################################################################
    # Constructor
    ####################################################################
    def __init__(self, *args, **kw):

        super(ClassesClass, self).__init__(*args, **kw)

        self.SetLabelBackgroundColour('#DBD4D4')

        self.InitUI()

    #    


    ####################################################################
    # Init the UI
    ####################################################################
    def InitUI(self):

        self.CreateGrid(1, 3)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnCellChanged)

        self.SetColLabelSize(40)
        self.SetRowLabelSize(80)

        self.SetColLabelValue(0, "Class")
        self.SetColLabelValue(1, "Name")
        self.SetColLabelValue(2, "Notes")

        self.classList = []
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
        Storage.FileIf.SetModified(True)

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
            self.SetCellValue(rowNo, 0, toks[0])   # Class
            self.SetCellValue(rowNo, 1, toks[1])   # Name
            self.SetCellValue(rowNo, 2, toks[2])   # Notes
            self.classList.append(toks[0])
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
        toks = [0] * 3

        rows = self.GetNumberRows()

        for iRow in range(rows):
            toks[0] = self.GetCellValue(iRow, 0)   # Class
            toks[1] = self.GetCellValue(iRow, 1)   # Name
            toks[2] = self.GetCellValue(iRow, 2)   # Notes
            data.append(list(toks))
        #
        return data
    #


    ####################################################################
    # Get a list of classes
    ####################################################################
    def GetList(self):
        return self.classList
    #

    ####################################################################
    # Get loaded data
    ####################################################################
    def GetData(self):
        return self.data
    #

    ####################################################################
    # Read the Class section from the HDQG file
    # Does not update the loaded data set
    ####################################################################
    def ImportFile(self, fp):

        data = []

        # Read the Column header line
        line = fp.readline().strip()

        if ("Class,Name,Notes" not in line):
            Storage.Logger.LogError("Missing Class column header")
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

            # Insure we have 3
            if (len(toks) != 3):
                Storage.Logger.LogError("Invalid number of columns in Class")
                return (False, [])
            else:
                data.append(toks)
            #
        #    

        return (True, data)

    #

    ####################################################################
    # Export the Class data to a CSV file
    # Does not update the loaded data set
    # Does not write the #CLASSES or #END tokens
    # Leaves the file open
    ####################################################################
    def ExportFile(self, fp, data):

        # Write header
        fp.write("Class,Name,Notes\n")

        # Write data
        for toks in data:
            s = "%s,%s,%s\n" % \
            (toks[0],
            toks[1],
            toks[2])
            fp.write(s)
        #

    #

#    

