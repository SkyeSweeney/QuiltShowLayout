
import wx
import wx.grid


#---------------------------------------------------------------------------

class QuiltsClass(wx.grid.Grid):

    ####################################################################
    #
    ####################################################################
    def __init__(self, *args, **kw):
        super(QuiltsClass, self).__init__(*args, **kw)

        self.SetLabelBackgroundColour('#DBD4D4')

        self.InitUI()
    #    


    ####################################################################
    #
    ####################################################################
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
        quilts = []
        self.LoadData(quilts)

    #    



    ####################################################################
    #
    ####################################################################
    def LoadData(self, quilts):


        numRows = len(quilts)

        self.BeginBatch()
            
        # Nuke the current grid
        if self.GetNumberRows() != 0:
            self.DeleteRows(0, self.GetNumberRows())

        # Size for the new grid
        self.InsertRows(0, numRows)

        rowNo = 0
        for toks in quilts:
            self.SetCellValue(rowNo,0, toks[0])   # Entry
            self.SetCellValue(rowNo,1, toks[1])   # Class
            self.SetCellValue(rowNo,2, toks[2])   # Width
            self.SetCellValue(rowNo,3, toks[3])   # Length
            self.SetCellValue(rowNo,4, toks[4])   # Notes
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

        rowNo = 0
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

#    

