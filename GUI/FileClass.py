



class FileClass:

    def __init__(self):
        pass
    #


    def read(self, fn):

        # Assume the operation will fail.
        retval = False

        fp = open(fn, "r")

        MODE_HDR            = 0
        MODE_QUILT_SEP      = 1
        MODE_QUILT_HDR      = 2
        MODE_QUILT_DATA     = 3
        MODE_RACKS_HDR      = 4
        MODE_RACKS_DATA     = 5
        MODE_OVERRIDES_HDR  = 6
        MODE_OVERRIDES_DATA = 7
        MODE_INVENTORY = 8
        MODE_ERROR = 9
        MODE_DONE = 10

        mode = MODE_HDR
        quilts = []
        racks = []
        overrides = []
        

        while True:

            # Insure the header is right
            line = fp.readline().strip()
            print(line)

            ########################################
            # HEADER
            ########################################
            if (mode == MODE_HDR):

                if (line != "#HDQG V1.0"):
                    print("Error: Invalid file type")
                    mode = MODE_ERROR
                else:
                    mode = MODE_QUILT_HDR
                #

            ##############################################
            # QUILT SEPERATOR
            ##############################################
            elif (mode == MODE_QUILT_SEP):

                if (line != "#QUILTS"):
                    print("Error: Missing #QUILTS")
                    mode = MODE_ERROR
                else:
                    mode = MODE_QUILT_HDR
                #

            ##############################################
            # QUILT HEADER
            ##############################################
            elif (mode == MODE_QUILT_HDR):

                if ("QID,Class,Width,Length,Notes" in line):
                    print("Error: Missing QID")
                    mode = MODE_ERROR
                else:    
                    mode = MODE_QUILT_DATA
                #

            ##############################################
            # QUILT DATA
            ##############################################
            elif (mode == MODE_QUILT_DATA):
                
                if (line == "#RACKS"):
                    mode = MODE_RACKS_HDR
                    print("Change to RACKS_HDR")
                else:
                    toks = line.split(",")
                    if (len(toks) != 5):
                        mode = MODE_ERROR
                    else:
                        quilts.append(toks)
                    #    
                #

            ##############################################
            # RACKS HEADER
            ##############################################
            elif (mode == MODE_RACKS_HDR):

                if ("RID,Row,Side,Bay" in line):
                    mode = MODE_RACKS_DATA
                else:    
                    print("Error: Missing RID2")
                    mode = MODE_ERROR

            ##############################################
            # RACKS DATA
            ##############################################
            elif (mode == MODE_RACKS_DATA):
                
                if (line == "#OVERRIDES"):
                    mode = MODE_OVERRIDES_HDR
                else:
                    toks = line.split(",")
                    if (len(toks) != 14):
                        mode = MODE_ERROR
                    else:
                        racks.append(toks)
                    #    
                #

            ##############################################
            # OVERRIDES HEADER
            ##############################################
            elif (mode == MODE_OVERRIDES_HDR):

                if ("QID,Row,Side,Bay,Level,Notes" in line):
                    mode = MODE_OVERRIDES_DATA
                else:    
                    print("Error: Missing QID")
                    mode = MODE_ERROR
                #    

            ##############################################
            # OVERRIDE DATA
            ##############################################
            elif (mode == MODE_OVERRIDES_DATA):
                
                if (line == "#INVENTORY"):
                    mode = MODE_DONE
                else:
                    toks = line.split(",")
                    if (len(toks) != 6):
                        mode = MODE_ERROR
                    else:
                        overrides.append(toks)
                    #    
                #

            ##############################################
            #
            ##############################################
            elif (mode == MODE_ERROR):
                print("Failed to read")
                del(quilts)
                del(racks)
                del(overrides)
                retval = False
                break

            ##############################################
            #
            ##############################################
            elif (mode == MODE_DONE):
                retval = True
                break
            #
        # While

        fp.close()


        return retval
    #
#

if __name__ == "__main__":

    obj = FileClass()
    ret = obj.read("Project.hdqg")
    print(ret)

