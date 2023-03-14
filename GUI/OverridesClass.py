
import wx
import wx.grid


#---------------------------------------------------------------------------

class OverridesClass(wx.grid.Grid):
    def __init__(self, *args, **kw):
        super(OverridesClass, self).__init__(*args, **kw)

        self.SetLabelBackgroundColour('#DBD4D4')

        self.InitUI()
    #    

    def InitUI(self):

        nOfRows = 400
        nOfCols = 6

        self.row = self.col = 0
        self.CreateGrid(nOfRows, nOfCols)

        self.SetColLabelSize(40)
        self.SetRowLabelSize(80)

        self.SetColLabelValue(0, "QID")
        self.SetColLabelValue(1, "Row")
        self.SetColLabelValue(2, "Side")
        self.SetColLabelValue(3, "Bay")
        self.SetColLabelValue(4, "Level")
        self.SetColLabelValue(5, "Notes")

        # Load file
        overrides = []
        self.LoadData(overrides)

    #    


    def LoadData(self, overrides):


        self.BeginBatch()

        # Nuke the current grid
        if self.GetNumberRows() != 0:
            self.DeleteRows(0, self.GetNumberRows())

        # Size for the new grid
        self.InsertRows(0, len(overrides))


        rowNo = 0
        for toks in overrides:
            self.SetCellValue(rowNo,0, toks[0])   # QID
            self.SetCellValue(rowNo,1, toks[1])   # Row
            self.SetCellValue(rowNo,2, toks[2])   # Side
            self.SetCellValue(rowNo,3, toks[3])   # Bay
            self.SetCellValue(rowNo,4, toks[4])   # Level
            self.SetCellValue(rowNo,5, toks[5])   # Notes
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
        toks = [0] * 6

        rows = self.GetNumberRows()

        rowNo = 0
        for iRow in range(rows):
            toks[0] = self.GetCellValue(iRow, 0)   # 
            toks[1] = self.GetCellValue(iRow, 1)   # 
            toks[2] = self.GetCellValue(iRow, 2)   # 
            toks[3] = self.GetCellValue(iRow, 3)   # 
            toks[4] = self.GetCellValue(iRow, 4)   # 
            toks[5] = self.GetCellValue(iRow, 5)   # 
            data.append(list(toks))
        #
        return data
    #


