
import os
import os.path
import Storage



########################################################################
# File handeling class
########################################################################
class FileClass:

    ####################################################################
    # Initialization
    ####################################################################
    def __init__(self):
        pass
        self.loaded = False
        self.modified = False
        self.fileName = ""
    #


    ####################################################################
    # Set/clear file modified flag
    ####################################################################
    def SetModified(self, b):
        self.modified = b
        if b:
            Storage.statusbar.SetStatusText("Modified", 0)
        else:
            Storage.statusbar.SetStatusText("Unchanged", 0)
    #

    ####################################################################
    # Get file modified flag
    ####################################################################
    def GetModified(self):
        return self.modified
    #


    ####################################################################
    # Set/clear file loaded flag
    ####################################################################
    def SetLoaded(self, b):
        self.loaded = b
    #


    ####################################################################
    # Get file loaded flag
    ####################################################################
    def GetLoaded(self):
        return self.loaded
    #

    ####################################################################
    # Set file name
    ####################################################################
    def SetFileName(self, fn):
        self.fileName = fn
        Storage.statusbar.SetStatusText(fn, 1)
    #


    ####################################################################
    # Get file name
    ####################################################################
    def GetFileName(self):
        return self.fileName
    #


    ####################################################################
    # Read a file and return the results in a tupple of lists
    # This does NOT load the data into the active storage
    ####################################################################
    def read(self, fn):

        # Assume the operation will fail.
        retval = False

        fp = open(fn, "r")

        MODE_HDR              = 0
        MODE_QUILT_START      = 1
        MODE_QUILT_HDR        = 2
        MODE_QUILT_DATA       = 3
        MODE_RACKS_START      = 4
        MODE_RACKS_HDR        = 5
        MODE_RACKS_DATA       = 6
        MODE_OVERRIDES_START  = 7
        MODE_OVERRIDES_HDR    = 8
        MODE_OVERRIDES_DATA   = 9
        MODE_CLASSES_START    = 10
        MODE_CLASSES_HDR      = 11
        MODE_CLASSES_DATA     = 12
        MODE_INI_START        = 13
        MODE_INI_DATA         = 14
        MODE_ERROR            = 15
        MODE_DONE             = 16

        self.setMode(MODE_HDR)
        quilts    = []
        racks     = []
        overrides = []
        classes   = []
        ini       = []
        

        while True:

            # Insure the header is right
            line = fp.readline().strip()
            #Storage.Logger.LogDebug(line)

            ########################################
            # FILE HEADER
            ########################################
            if (self.mode == MODE_HDR):

                if (line != "#HDQG V1.0"):
                    Storage.Logger.LogError("Error: Invalid file type")
                    self.setMode(MODE_ERROR)
                else:
                    self.setMode(MODE_QUILT_START)
                #

            ##############################################
            # QUILT START
            ##############################################
            elif (self.mode == MODE_QUILT_START):

                if (line != "#QUILTS"):
                    Storage.Logger.LogError("Error: Missing #QUILTS")
                    self.setMode(MODE_ERROR)
                else:
                    self.setMode(MODE_QUILT_HDR)
                #

            ##############################################
            # QUILT HEADER
            ##############################################
            elif (self.mode == MODE_QUILT_HDR):

                if ("QID,Class,Width,Length,Notes" in line):
                    self.setMode(MODE_QUILT_DATA)
                else:
                    Storage.Logger.LogError(line)
                    Storage.Logger.LogError("Error: Missing QID")
                    self.setMode(MODE_ERROR)
                #

            ##############################################
            # QUILT DATA
            ##############################################
            elif (self.mode == MODE_QUILT_DATA):
                
                if (line == "#END"):
                    self.setMode(MODE_RACKS_START)
                else:
                    toks = line.split(",")
                    if (len(toks) != 5):
                        Storage.Logger.LogError("C")
                        self.setMode(MODE_ERROR)
                    else:
                        quilts.append(toks)
                    #    
                #

            ##############################################
            # RACKS START
            ##############################################
            elif (self.mode == MODE_RACKS_START):

                if (line != "#RACKS"):
                    Storage.Logger.LogError("Error: Missing #RACKS")
                    self.setMode(MODE_ERROR)
                else:
                    self.setMode(MODE_RACKS_HDR)
                #

            ##############################################
            # RACKS HEADER
            ##############################################
            elif (self.mode == MODE_RACKS_HDR):

                if ("RID,Row,Side,Bay" in line):
                    self.setMode(MODE_RACKS_DATA)
                else:    
                    Storage.Logger.LogError("Error: Missing RID2")
                    self.setMode(MODE_ERROR)

            ##############################################
            # RACKS DATA
            ##############################################
            elif (self.mode == MODE_RACKS_DATA):
                
                if (line == "#END"):
                    self.setMode(MODE_OVERRIDES_START)
                else:
                    toks = line.split(",")
                    if (len(toks) != 14):
                        Storage.Logger.LogError("B")
                        self.setMode(MODE_ERROR)
                    else:
                        racks.append(toks)
                    #    
                #

            ##############################################
            # OVERRIDES START
            ##############################################
            elif (self.mode == MODE_OVERRIDES_START):

                if (line != "#OVERRIDES"):
                    Storage.Logger.LogError("Error: Missing #RACKS")
                    self.setMode(MODE_ERROR)
                else:
                    self.setMode(MODE_OVERRIDES_HDR)
                #

            ##############################################
            # OVERRIDES HEADER
            ##############################################
            elif (self.mode == MODE_OVERRIDES_HDR):

                if ("QID,Row,Side,Bay,Level,Notes" in line):
                    self.setMode(MODE_OVERRIDES_DATA)
                else:    
                    Storage.Logger.LogError("Error: Missing QID in overrides")
                    self.setMode(MODE_ERROR)
                #    

            ##############################################
            # OVERRIDE DATA
            ##############################################
            elif (self.mode == MODE_OVERRIDES_DATA):
                
                if (line == "#END"):
                    self.setMode(MODE_CLASSES_START)
                else:
                    toks = line.split(",")
                    if (len(toks) != 6):
                        Storage.Logger.LogError("A")
                        self.setMode(MODE_ERROR)
                    else:
                        overrides.append(toks)
                    #    
                #

            ##############################################
            # CLASSES START
            ##############################################
            elif (self.mode == MODE_CLASSES_START):

                if (line != "#CLASSES"):
                    Storage.Logger.LogError("Error: Missing #CLASSES")
                    self.setMode(MODE_ERROR)
                else:
                    self.setMode(MODE_CLASSES_HDR)
                #

            ##############################################
            # CLASSES HEADER
            ##############################################
            elif (self.mode == MODE_CLASSES_HDR):

                if ("Class,Name,Notes" in line):
                    self.setMode(MODE_CLASSES_DATA)
                else:    
                    Storage.Logger.LogError("Error: Missing Class")
                    self.setMode(MODE_ERROR)
                #    

            ##############################################
            # CLASSES DATA
            ##############################################
            elif (self.mode == MODE_CLASSES_DATA):
                
                if (line == "#END"):
                    self.setMode(MODE_INI_START)
                else:
                    toks = line.split(",")
                    if (len(toks) != 3):
                        Storage.Logger.LogError("D")
                        self.setMode(MODE_ERROR)
                    else:
                        classes.append(toks)
                    #    
                #

            ##############################################
            # INI START
            ##############################################
            elif (self.mode == MODE_INI_START):

                if (line != "#INI"):
                    Storage.Logger.LogError("Error: Missing #INI")
                    self.setMode(MODE_ERROR)
                else:
                    self.setMode(MODE_INI_DATA)
                #

            ##############################################
            # INI DATA
            ##############################################
            elif (self.mode == MODE_INI_DATA):
                
                if (line == "#END"):
                    self.setMode(MODE_DONE)
                else:
                    ini.append(line)
                #

            ##############################################
            # An Error happened
            ##############################################
            elif (self.mode == MODE_ERROR):

                # Clean up the mess
                quilts.clear()
                racks.clear()
                overrides.clear()
                classes.clear()
                ini.clear()
                retval = False
                break

            ##############################################
            # We finished
            ##############################################
            elif (self.mode == MODE_DONE):
                retval = True
                break
            #
        # do forever

        fp.close()


        return (retval, quilts, racks, overrides, classes, ini)
    # read

    ####################################################################
    # Routine to aid debuging
    ####################################################################
    def setMode(self, mode):
        Storage.Logger.LogDebug("Change to mode %d" % mode)
        self.mode = mode
    #    

    ####################################################################
    # Write a file given a set of lists
    ####################################################################
    def write(self, fn, quilts, racks, overrides, classes, ini):

        # Assume the operation will fail.
        retval = False

        # Open the file
        fp = open(fn, "w")

        # Write the file header
        fp.write("#HDQG V1.0\n")

        # Write quilt data
        fp.write("#QUILTS\n")
        fp.write("QID,Class,Width,Length,Notes\n")
        for toks in quilts:
            s = "%s,%s,%s,%s,%s\n" % (toks[0], toks[1], toks[2], toks[3], toks[4])
            fp.write(s)
        #
        fp.write("#END\n")

        # Write racks data
        fp.write("#RACKS\n")
        fp.write("RID,Row,Side,Bay,Dxf Bay,Level,SlatW,ActWidth,ActHeight,Left Pole,Right Pole,Class,H-Tol,Notes\n")
        for toks in racks:
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
        fp.write("#END\n")

        # Write override data
        fp.write("#OVERRIDES\n")
        fp.write("QID,Row,Side,Bay,Level,Notes\n")
        for toks in overrides:
            s = "%s,%s,%s,%s,%s,%s\n" % \
            (toks[0],
            toks[1],
            toks[2],
            toks[3],
            toks[4],
            toks[5])
            fp.write(s)
        #
        fp.write("#END\n")

        # Write CLASSES data
        fp.write("#CLASSES\n")
        Storage.ClassesC.ExportFile(fp, classes)
        fp.write("#END\n")

        # Write INI data
        fp.write("#INI\n")
        for line in ini:
            s = "%s\n" % line
            fp.write(s)
        #

        fp.write("#END\n")

        fp.close()

        # If we made it here we stored the file!

        return True

    # read
#


#
# Test routine
#
if __name__ == "__main__":

    obj = FileClass()
    (ret, quilts, racks, overrides, classes, ini) = obj.read("Project.hdqg")
    print("Read", ret)
    ret = obj.write("new.hdqg", quilts, racks, overrides, classes, ini)
    print("Write", ret)


