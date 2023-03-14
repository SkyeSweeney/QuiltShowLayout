
import wx
import wx.grid


#---------------------------------------------------------------------------

class RacksClass(wx.grid.Grid):
    def __init__(self, *args, **kw):
        super(RacksClass, self).__init__(*args, **kw)

        self.SetLabelBackgroundColour('#DBD4D4')

        self.InitUI()
    #    

    def InitUI(self):

        nOfRows = 300
        nOfCols = 14

        self.row = self.col = 0
        self.CreateGrid(nOfRows, nOfCols)

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
        racks = []
        self.LoadData(racks)

    #    


    ####################################################################
    # Load the table from a list of racks
    ####################################################################

    def LoadData(self, racks):


        self.BeginBatch()

        # Nuke the current grid
        if self.GetNumberRows() != 0:
            self.DeleteRows(0, self.GetNumberRows())

        # Size for the new grid
        self.InsertRows(0, len(racks))


        rowNo = 0
        for toks in racks:
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


