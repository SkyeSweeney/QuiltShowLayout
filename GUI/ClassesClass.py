
import wx
import wx.grid


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

        nOfRows = 0
        nOfCols = 3

        self.row = self.col = 0
        self.CreateGrid(nOfRows, nOfCols)

        self.SetColLabelSize(40)
        self.SetRowLabelSize(80)

        self.SetColLabelValue(0, "Class")
        self.SetColLabelValue(1, "Name")
        self.SetColLabelValue(2, "Notes")

        self.classList = []

        # Load file
        self.LoadFile("Classes.csv")

    #    



    ####################################################################
    # Load the table from a list of lines
    ####################################################################
    def LoadLines(self, lines):

        self.BeginBatch()

        # Nuke the current grid
        if self.GetNumberRows() != 0:
            self.DeleteRows(0, self.GetNumberRows())

        # Size for the new grid
        self.InsertRows(0, len(lines))

        rowNo = 0
        for line in lines:
            toks = line.strip().split(",")
            self.SetCellValue(rowNo, 0, toks[0])   # Class
            self.SetCellValue(rowNo, 1, toks[1])   # Name
            self.SetCellValue(rowNo, 2, toks[2])   # Notes
            if (toks[0] in self.classList):
                print("Error: Class %s duplicated in file" % toks[0])
            else:
                self.classList.append(toks[0])
            #
            rowNo += 1
        #
        self.EndBatch()
        self.ForceRefresh()
    #


    ####################################################################
    # Get a list of classes
    ####################################################################
    def GetList(self):
        return self.classList
    #

#    

