
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

        # Load file
        self.LoadData(self.classList)
    #


    ####################################################################
    # Called when cell changes value
    ####################################################################
    def OnCellChanged(self, event):

        row = event.GetRow()
        col = event.GetCol()
        was = event.GetString() # Original value
        now = self.GetCellValue(row, col) # New value
        print("Changed", row, col, was, now)

        # Check the validity of the change

        # Mark file as changed
        Storage.FileIf.SetModified(True)

     #



    ####################################################################
    # Load the table from a list of lines
    ####################################################################
    def LoadData(self, classes):

        self.BeginBatch()

        # Nuke the current grid
        if self.GetNumberRows() != 0:
            self.DeleteRows(0, self.GetNumberRows())

        # Size for the new grid
        self.InsertRows(0, len(classes))

        rowNo = 0
        for toks in classes:
            self.SetCellValue(rowNo, 0, toks[0])   # Class
            self.SetCellValue(rowNo, 1, toks[1])   # Name
            self.SetCellValue(rowNo, 2, toks[2])   # Notes
            self.classList.append(toks[0])
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

#    

