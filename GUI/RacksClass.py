
import wx
import wx.grid
import Storage


#---------------------------------------------------------------------------

class RacksClass(wx.grid.Grid):
    ####################################################################
    # Constructor
    ####################################################################
    def __init__(self, *args, **kw):
        super(RacksClass, self).__init__(*args, **kw)

        self.SetLabelBackgroundColour('#DBD4D4')

        self.loaded = False
        self.modified = False

        self.InitUI()
    #    

    ####################################################################
    # Init the UI
    ####################################################################
    def InitUI(self):

        self.CreateGrid(1, 14)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnCellChanged)

        self.SetColLabelSize(40)
        self.SetRowLabelSize(80)

        self.SetColLabelValue(0, "ID")
        self.SetColLabelValue(1, "Row")
        self.SetColLabelValue(2, "Side")
        self.SetColLabelValue(3, "Bay")
        self.SetColLabelValue(4, "DXF Bay")
        self.SetColLabelValue(5, "Level")
        self.SetColLabelValue(6, "Slat Width")
        self.SetColLabelValue(7, "Actual Width")
        self.SetColLabelValue(8, "Actual Height")
        self.SetColLabelValue(9, "Left Pole")
        self.SetColLabelValue(10, "Right Pole")
        self.SetColLabelValue(11, "Class")
        self.SetColLabelValue(12, "H Tolelrance")
        self.SetColLabelValue(13, "Notes")

        # Load file
        self.data = []
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
            self.SetCellValue(rowNo,0,  toks[0])    # ID
            self.SetCellValue(rowNo,1,  toks[1])    # Row
            self.SetCellValue(rowNo,2,  toks[2])    # Side
            self.SetCellValue(rowNo,3,  toks[3])    # Bay
            self.SetCellValue(rowNo,4,  toks[4])    # DXF Bay
            self.SetCellValue(rowNo,5,  toks[5])    # Level
            self.SetCellValue(rowNo,6,  toks[6])    # Slat Width
            self.SetCellValue(rowNo,7,  toks[7])    # Actual Width
            self.SetCellValue(rowNo,8,  toks[8])    # Actual Height
            self.SetCellValue(rowNo,9,  toks[9])    # Left Pole
            self.SetCellValue(rowNo,10, toks[10])   # Right Pole
            self.SetCellValue(rowNo,11, toks[11])   # Class
            self.SetCellValue(rowNo,12, toks[12])   # H Tolerance
            self.SetCellValue(rowNo,13, toks[13])   # Notes
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
        toks = [0] * 14

        rows = self.GetNumberRows()

        for iRow in range(rows):
            toks[0]  = self.GetCellValue(iRow, 0)   # 
            toks[1]  = self.GetCellValue(iRow, 1)   # 
            toks[2]  = self.GetCellValue(iRow, 2)   # 
            toks[3]  = self.GetCellValue(iRow, 3)   # 
            toks[4]  = self.GetCellValue(iRow, 4)   # 
            toks[5]  = self.GetCellValue(iRow, 5)   # 
            toks[6]  = self.GetCellValue(iRow, 6)   # 
            toks[7]  = self.GetCellValue(iRow, 7)   # 
            toks[8]  = self.GetCellValue(iRow, 8)   # 
            toks[9]  = self.GetCellValue(iRow, 9)   # 
            toks[10] = self.GetCellValue(iRow, 10)  # 
            toks[11] = self.GetCellValue(iRow, 11)  # 
            toks[12] = self.GetCellValue(iRow, 12)  # 
            toks[13] = self.GetCellValue(iRow, 13)  # 
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

        if "RID,Row,Side,Bay,Dxf Bay,Level,SlatW,ActWidth,ActHeight,Left Pole,Right Pole,Class,H-Tol,Notes" not in line:
            Storage.Logger.LogError("Missing Racks column header")
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

            # Insure we have 14
            if (len(toks) != 14):
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
        fp.write("RID,Row,Side,Bay,Dxf Bay,Level,SlatW,ActWidth,ActHeight,Left Pole,Right Pole,Class,H-Tol,Notes\n")


        # Write data
        for toks in data:
            s = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % \
            (toks[0],
            toks[1],
            toks[2],
            toks[3],
            toks[4],
            toks[5],
            toks[6],
            toks[7],
            toks[8],
            toks[9],
            toks[10],
            toks[11],
            toks[12],
            toks[13])
            fp.write(s)
        #

    #

#    

