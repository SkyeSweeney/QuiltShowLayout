
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
        self.LoadFile("Quilts.csv")

    #    



    ####################################################################
    #
    ####################################################################
    def LoadFile(self, fn):

        fp = open(fn, "r")

        l = []

        numRows = 0
        for line in fp:
            toks = line.strip().split(",")
            if len(toks[0]) == 0:
                continue
            if (toks[0] == "Entry #"):
                continue
            if (toks[0][0] == "#"):
                continue
            l.append(toks)


            numRows += 1
        #
        fp.close()

        self.BeginBatch()
            
        # Nuke the current grid
        if self.GetNumberRows() != 0:
            self.DeleteRows(0, self.GetNumberRows())

        # Size for the new grid
        self.InsertRows(0, numRows)

        rowNo = 0
        for toks in l:
            self.SetCellValue(rowNo,0, toks[0])   # Entry
            self.SetCellValue(rowNo,1, toks[1])   # Class
            self.SetCellValue(rowNo,2, toks[2])   # Width
            self.SetCellValue(rowNo,3, toks[3])   # Length
            self.SetCellValue(rowNo,4, toks[4])   # Notes

            if toks[0] in l:
                print("Error: Duplicate quilt ID %s in file" % toks[0])
            #
            rowNo += 1
        #
        self.EndBatch()
        self.ForceRefresh()
    #

