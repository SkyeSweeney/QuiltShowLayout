
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
        self.LoadFile("Overrides.csv")

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
            self.SetCellValue(rowNo,0, toks[0])   # QID
            self.SetCellValue(rowNo,1, toks[1])   # Row
            self.SetCellValue(rowNo,2, toks[2])   # Side
            self.SetCellValue(rowNo,3, toks[3])   # Bay
            self.SetCellValue(rowNo,4, toks[4])   # Level
            self.SetCellValue(rowNo,5, toks[5])   # Notes
            rowNo += 1
        #
        fp.close()
        self.EndBatch()
        self.ForceRefresh()
    #

