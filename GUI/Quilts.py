
import wx
import wx.grid


#---------------------------------------------------------------------------

class Quilts(wx.grid.Grid):
    def __init__(self, *args, **kw):
        super(Quilts, self).__init__(*args, **kw)

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

