
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
        self.fileName = ""
    #

    ####################################################################
    # Set file modified flag
    ####################################################################
    def SetAllModified(self, b):
        Storage.QuiltsC.modifed = b
        Storage.RacksC.modifed  = b
        Storage.ClassesC.modifed  = b
        Storage.OverridesC.modifed = b
        return 
    #


    ####################################################################
    # Get file modified flag
    ####################################################################
    def GetAnyModified(self):
        modified = Storage.QuiltsC.modifed and \
                   Storage.RacksC.modifed and \
                   Storage.ClassesC.modifed and \
                   Storage.OverridesC.modifed
        return modified
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
        MODE_QUILTS_SECTION   = 1
        MODE_RACKS_SECTION    = 2
        MODE_OVERRIDES_START  = 7
        MODE_OVERRIDES_HDR    = 8
        MODE_OVERRIDES_DATA   = 9
        MODE_CLASSES_SECTION  = 10
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

            # Read the next line of the file
            line = fp.readline().strip()
            Storage.Logger.LogDebug(line)


            ########################################
            # FILE HEADER
            ########################################
            if (self.mode == MODE_HDR):

                if (line != "#HDQG V1.0"):
                    Storage.Logger.LogError("Invalid file type")
                    self.setMode(MODE_ERROR)
                else:
                    self.setMode(MODE_QUILTS_SECTION)
                #

            ##############################################
            # QUILTS SECTION
            ##############################################
            elif (self.mode == MODE_QUILTS_SECTION):

                # If the QUILTS token
                if (line == "#QUILTS"):

                    # Read this section of the file
                    (ok, quilts) = Storage.QuiltsC.ImportFile(fp)

                    # If read was OK, go read the next section
                    if ok:
                        self.setMode(MODE_RACKS_SECTION)
                    else:
                        Storage.Logger.LogError("Unable to read Quilt")
                        self.setMode(MODE_ERROR)
                    #
                else:
                    Storage.Logger.LogError("Missing #QUILTS")
                    self.setMode(MODE_ERROR)
                #    


            ##############################################
            # RACKS START
            ##############################################
            elif (self.mode == MODE_RACKS_SECTION):

                if (line == "#RACKS"):

                    # Read this section of the file
                    (ok, racks) = Storage.RacksC.ImportFile(fp)

                    # If read was OK, go read the next section
                    if ok:
                        self.setMode(MODE_OVERRIDES_START)
                    else:
                        Storage.Logger.LogError("Unable to read Racks")
                        self.setMode(MODE_ERROR)
                    #
                else:
                    Storage.Logger.LogError("Missing #RACKS")
                    self.setMode(MODE_ERROR)
                #    

            ##############################################
            # OVERRIDES START
            ##############################################
            elif (self.mode == MODE_OVERRIDES_START):

                if (line != "#OVERRIDES"):
                    Storage.Logger.LogError("Missing #RACKS")
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
                    Storage.Logger.LogError("Missing QID in overrides")
                    self.setMode(MODE_ERROR)
                #    

            ##############################################
            # OVERRIDE DATA
            ##############################################
            elif (self.mode == MODE_OVERRIDES_DATA):
                
                if (line == "#END"):
                    self.setMode(MODE_CLASSES_SECTION)
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
            elif (self.mode == MODE_CLASSES_SECTION):

                # If the Class token
                if (line == "#CLASSES"):

                    # Read this section of the file
                    (ok, classes) = Storage.ClassesC.ImportFile(fp)

                    # If read was OK, go read the INI section
                    if ok:
                        self.setMode(MODE_INI_START)
                    else:
                        Storage.Logger.LogError("Unable to read Classes")
                        self.setMode(MODE_ERROR)
                    #
                else:
                    Storage.Logger.LogError("Missing #CLASSES")
                    self.setMode(MODE_ERROR)
                #    


            ##############################################
            # INI START
            ##############################################
            elif (self.mode == MODE_INI_START):

                if (line != "#INI"):
                    Storage.Logger.LogError("Missing #INI")
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


            # We got an unexpected EOF
            if line == "":
                Storage.Logger.LogError("Unexpected EOF")
                break
            #

        # do forever

        fp.close()


        return (retval, quilts, racks, overrides, classes, ini)

    #

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


