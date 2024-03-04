#! /usr/bin/python

"""
########################################################################
#
# Program to arrange quilts onto racks for a quilt show
# Program is used to help automate the placement of quilts on racks
# for the quilt show given by the Hannah Dustin Quilt Guild.
#
# History:
# Originally written in 2015 when Jessie Sweenmey took over setup.
# The previous guild member had a different methodology but was unable
# to share due to health issues. Jessie had started to try to lay it
# out with paper and pencil on graph paper but soon realized the
# difficulty in this. Skye started to help by writting this program
# to follow a few simple rules that Jessie had come up with. These
# were centered on getting large quilts on large racks, similar sized
# quilts on slats with more than one quilt and similar length quilts
# when placed back to back. The rules alse were to force only using
# racks that were available and in the space available.
#
# Documentation:
# In this repo you should find a word document with documentation on
# how to run the program and some hints to how to layout the show.
#
# Software documentation:
# I hope the comments in the code are of some help.
# The basic approach is to read a few CSV files, try to find a place
# for each quilt, then print various lists detailing the placement,
# as well as some CAD files showing the placements graphicaly. 
#
# If the placement of the quilts does not match you needs, you can
# force a quilt to a given place by using the overrides file. 
#
# The function 'Process' is were the assignment loop starts.
#
# Note that the order the quilts are listed in the Overrides and
# quilts file is important. The first quilt in the overrides file
# goes to the first spot on that rack (if more than on quilt on a 
# rack). So if you want to exchange positions of two quilts on a
# single slat, you need to change the order in the CSV file. The
# same thing holds true for the Quilts file. They will get placed
# in order.
#
# There is some complexity when printing CAD (DXF) files. You can
# print then as if you were standing in the hall looking at the quilts
# or you can print them in "back to back" format to more easily
# visualize how the quilts like up back to back. This adds considerable
# shenanigans to the code.
#
# Written by: (Patrick) Skye Sweeney
#
########################################################################
"""

import sys
import math
import argparse
from operator import itemgetter
from dxfwrite import DXFEngine as dxf

# Columns in the QUILT CSV file
Q_ID     = 0  # The quilt ID
Q_CLASS  = 1  # The quilts class
Q_WIDTH  = 2  # The width of the quilt
Q_HEIGHT = 3  # The heigth of the quilt
Q_SLAT   = 4  # Not in CSV. Used in program

# Columns in the RACKS CSV file
R_ID     = 0  # The row ID
R_ROW    = 1  # The human row number
R_SIDE   = 2  # The side (front or back)
R_RBAY   = 3  # The bay in a series of racks
R_DXFBAY = 4  # The bay used for producing DXF files
R_LEVEL  = 5  # The level (top, mid)
R_SWIDTH = 6   # Slat width used for bay
R_RWIDTH = 7   # Real width between poles
R_HEIGHT = 8   # Heigth of the quilt
R_LEFT   = 9   # Height of pole to left
R_RIGHT  = 10  # Height of pole to right
R_CLASS  = 11     # Categorry class of quilt to be alloed on rack
R_TOLERANCE = 12  # Percent tolerance for quilt heights on same rack
R_REMAIN    = 13  # Not in CSV. Used by program
R_QUILTS    = 14  # Not in CSV. Used by program

# Columns in the Overrides file
O_QID   = 0   # Quilt ID
O_ROW   = 1   # Row ID the quilt must be placed in
O_SIDE  = 2   # Size ID the quilt must be placed in
O_BAY   = 3   # Bay ID the quilt must be placed in
O_LEVEL = 4   # Level ID the quilt must tbe placed in


########################################################################
#
########################################################################
class QuiltApp():
    """ This class is the whole of the program. It is too long according
        to PEP8, but I prefer that then slipping the file for such a
        simple program. """

    ######################################################################
    ######################################################################
    def __init__(self):
        """ Initialization """

        # Parse command line arguments
        parser = argparse.ArgumentParser(description='command parser')
        parser.add_argument('--verbose',
                            action='store_const',
                            const=True,
                            dest='verbose',
                            default=False,
                            help="Verbose")
        parser.add_argument('--nodetail',
                            action='store_const',
                            const=True,
                            dest='nodetail',
                            default=False,
                            help="Remove detail from quilt DXF")
        parser.add_argument('--l2r',
                            action='store_const',
                            const=True,
                            dest='l2r',
                            default=False,
                            help="Print DXF right to left")
        parser.add_argument('--nodxf',
                            action='store_const',
                            const=True,
                            dest='nodxf',
                            default=False,
                            help="Do not generate DXF files")
        parser.add_argument('--rack',
                            action='store_const',
                            const=True,
                            dest='show_racks',
                            default=False,
                            help="Print rack info")

        stuff = parser.parse_args()
        self.nodetail = stuff.nodetail    # Print more detail on each quilt
        self.left_to_right = stuff.l2r
        self.nodxf = stuff.nodxf
        self.show_racks = stuff.show_racks

        self.quilts = []
        self.racks = []
        self.overrides = []

        if not self.left_to_right:
            self.right_bay = R_DXFBAY   # Print back to back
            print("Printing back to back")
        else:
            self.right_bay = R_RBAY     # Print for printed labels
            print("Printing left to right")
        #
    #

    #####################################################################
    #####################################################################
    def read_quilts(self):
        """ Read in quilt information """

        ###########################
        # Read in quilt information
        ###########################
        print("Reading in Quilts")
        fp_quilts = open("Quilts.csv", "r", encoding='utf-8')

        # Read off header
        line = fp_quilts.readline().strip()

        line_num = 1
        while True:

            line = fp_quilts.readline()
            if line == "":
                break

            toks = line.strip().split(",")
            if toks[0] == "":
                continue

            # Allow for commenting out a quilt
            if toks[0][0:1] == '#':
                print(f"Quilt {toks[0]} commented out")
                continue
            #

            try:
                self.quilts.append([toks[Q_ID],
                                    toks[Q_CLASS],
                                    float(toks[Q_WIDTH]),
                                    float(toks[Q_HEIGHT]),
                                    0])  # Slat
            except:
                print(f"Error on Quilts line {line_num}")
            #
            line_num = line_num + 1
        #
        fp_quilts.close()
    #

    #####################################################################
    #####################################################################
    def read_racks(self):
        """ Read in rack information """

        print("Reading in racks")
        fp_racks = open("Racks.csv", "r", encoding='utf-8')

        # Read off header
        line = fp_racks.readline().strip()

        line_num = 0
        while True:

            line_num = line_num + 1

            line = fp_racks.readline()
            if line == "":
                break

            toks = line.strip().split(",")
            if toks[0] == "":
                continue

            if toks[0] == "#":
                continue

            assigned_quilts = []

            try:
                rack = [int(toks[R_ID]),
                        int(toks[R_ROW]),
                        toks[R_SIDE],
                        int(toks[R_RBAY]),
                        int(toks[R_DXFBAY]),
                        toks[R_LEVEL],
                        float(toks[R_SWIDTH]),
                        float(toks[R_RWIDTH]),
                        float(toks[R_HEIGHT])*12,
                        int(toks[R_LEFT]),
                        int(toks[R_RIGHT]),
                        toks[R_CLASS],
                        float(toks[R_TOLERANCE]),
                        float(toks[R_RWIDTH]),   # REMAIN width on rack
                        assigned_quilts]          # Assigned quilts to rack

                self.racks.append(rack)

            except:
                print(f"Error: Conversion error in Racks line {line_num}")
                sys.exit(1)
            #

            # Sanity check items
            if (rack[R_SIDE] != 'Front') and (rack[R_SIDE] != 'Back'):
                print(f"Error: Bad side name in Racks line {line_num}")
                sys.exit(1)
            #

            if (rack[R_LEVEL] != 'Top') and (rack[R_LEVEL] != 'Mid'):
                print(f"Error: Bad level name in Racks line {line_num}")
                sys.exit()
            #

        #
        fp_racks.close()
    #

    #####################################################################
    #####################################################################
    def read_overrides(self):
        """ Read in override information """

        print("Reading in overrides")
        fp_overrides = open("Overrides.csv", "r", encoding='utf-8')

        # Read off header
        line = fp_overrides.readline().strip()

        line_num = 1
        while True:

            line = fp_overrides.readline()
            if line == "":
                break

            toks = line.strip().split(",")
            if toks[0] == "":
                continue

            try:
                over = [toks[O_QID],
                        int(toks[O_ROW]),
                        toks[O_SIDE],
                        int(toks[O_BAY]),
                        toks[O_LEVEL]]

                self.overrides.append(over)

            except:
                print(f"Error: Conversion error in Overrides line {line_num}")
                sys.exit(1)
            #

            # Sanity check items
            if (over[O_SIDE] != 'Front') and (over[O_SIDE] != 'Back'):
                print(f"Error: Bad side name in Overrides line {line_num}")
                sys.exit(1)
            #

            if (over[O_LEVEL] != 'Top') and (over[O_LEVEL] != 'Mid'):
                print(f"Error: Bad level name in Overrides line {line_num}")
                sys.exit()
            #

            line_num = line_num + 1
        #
        fp_overrides.close()
    #

    #####################################################################
    #####################################################################
    def create_quilt_list(self):
        """  Create the Quilt list
             CSV with the following format:
             Quilt, row, side, bay, level """

        print("Generating QuiltList.csv")

        fp_quilt_list = open("QuiltList.csv", "w", encoding='utf-8')

        fp_quilt_list.write("Quilt, Row, Side, Bay, Level\n")

        temp = []

        # Create list
        for rack in self.racks:
            for qid in rack[R_QUILTS]:
                temp.append((qid, rack[R_ROW], rack[R_SIDE],
                            rack[self.right_bay], rack[R_LEVEL]))
            #
        #

        # Sort list by qid (the zeroth element of the temp tupple)
        temp = sorted(temp, key=itemgetter(0))

        # Print list
        for i in temp:
            txt = f"{i[0]}, {i[1]}, {i[2]}, {i[3]}, {i[4]}\n"
            fp_quilt_list.write(txt)
        #

        fp_quilt_list.close()

    #

    #####################################################################
    #####################################################################
    def create_row_list(self):
        """  Create the Row list
             CSV with the following format:
             row, side, bay, level, quilt"""

        print("Generating RowList.csv")

        fp_row_list = open("RowList.csv", "w", encoding='utf-8')

        fp_row_list.write("Row, Side, Bay, Level, Quilt\n")

        temp = []

        # Create list
        for rack in self.racks:
            for qid in rack[R_QUILTS]:
                temp.append((qid, rack[R_ROW], rack[R_SIDE],
                            rack[self.right_bay], rack[R_LEVEL]))
            #
        #

        # Sort list first by qid, then by row, then side, and then by bay
        temp = sorted(temp, key=itemgetter(1, 2, 3, 4))

        # Print list
        for i in temp:
            txt = f"{i[1]}, {i[2]}, {i[3]}, {i[4]}, {i[0]}\n"
            fp_row_list.write(txt)
        #

        fp_row_list.close()

    #

    #####################################################################
    #####################################################################
    def print_racks(self):
        """  Print racks """

        for rack in self.racks:

            if rack[R_CLASS] == 'X':
                continue

            txt = "%2d %2d %1s %d %1s %2d %3d %2d %2d %3s %6.2f" % \
                (rack[R_ID],
                 rack[R_ROW],
                 rack[R_SIDE][0],
                 rack[R_RBAY],
                 rack[R_LEVEL][0],
                 rack[R_SWIDTH],
                 rack[R_HEIGHT]/12,
                 rack[R_LEFT],
                 rack[R_RIGHT],
                 rack[R_CLASS],
                 rack[R_TOLERANCE])

            for qid in rack[R_QUILTS]:
                txt = txt + " " + qid
            #
            print(txt)

        #
    #

    #####################################################################
    #####################################################################
    def print_materials(self):
        """  Print Materials """

        slats = {}
        slats[6] = 0
        slats[7] = 0
        slats[8] = 0
        slats[9] = 0
        slats[10] = 0
        slats[12] = 0

        inventory_slats = {}
        inventory_slats[6] = 39
        inventory_slats[7] = 3
        inventory_slats[8] = 85
        inventory_slats[9] = 10
        inventory_slats[10] = 34
        inventory_slats[12] = 13

        # Actual
        poles = {}
        poles[3] = 0
        poles[6] = 0
        poles[7] = 0
        poles[8] = 0
        poles[9] = 0
        poles[10] = 0
        poles[11] = 0

        # Inventory
        inventory_poles = {}
        inventory_poles[3] = 100
        inventory_poles[6] = 4
        inventory_poles[7] = 19
        inventory_poles[8] = 40
        inventory_poles[9] = 25
        inventory_poles[10] = 3
        inventory_poles[11] = 100

        inventory_bases = 83

        print("")
        print("Bill of materials:")

        # Set a last value that will be different on first pass
        last = self.racks[len(self.racks)-1]

        # For each rack
        for rack in self.racks:

            # Skip if the 'X' (deleted) class
            if rack[R_CLASS] == 'X':
                continue

            # If we changed row/side
            if (rack[R_ROW] != last[R_ROW]) or \
               (rack[R_SIDE] != last[R_SIDE]):

                # Add left pole
                if rack[R_SIDE] == 'Front':
                    poles[rack[R_LEFT]] = poles[rack[R_LEFT]] + 1

                # Add right pole
                if rack[R_SIDE] == 'Front':
                    poles[rack[R_RIGHT]] = poles[rack[R_RIGHT]] + 1

                # Add slat
                slats[rack[R_SWIDTH]] = slats[rack[R_SWIDTH]] + 1

            # Same row/side
            else:

                # If we changed bays
                if rack[self.right_bay] != last[self.right_bay]:

                    # Add right pole
                    if rack[R_SIDE] == 'Front':
                        poles[rack[R_RIGHT]] = poles[rack[R_RIGHT]] + 1

                    # Add slat
                    slats[rack[R_SWIDTH]] = slats[rack[R_SWIDTH]] + 1

                # We must have changed levels
                else:
                    # Add slat
                    slats[rack[R_SWIDTH]] = slats[rack[R_SWIDTH]] + 1
                #

            #

            # Save last values
            last = rack

        #

        for ndx in slats:
            extra = inventory_slats[ndx] - slats[ndx]
            if extra == 0:
                msg = "(WARNING EXACT COUNT)"
            elif extra == 1:
                msg = "(CAUTION, ONLY 1 SPARE)"
            elif extra < 0:
                msg = f"(ERROR: {-extra} TOO MANY ALLOCATED)"
            else:
                msg = ""
            #
            print(f"Slat {ndx} = {slats[ndx]}/{inventory_slats[ndx]} {msg}")
        #

        bases = 0
        for ndx in poles:
            extra = inventory_poles[ndx] - poles[ndx]
            if extra == 0:
                msg = "(WARNING EXACT COUNT)"
            elif extra == 1:
                msg = "(CAUTION, ONLY 1 SPARE)"
            elif extra < 0:
                msg = f"(ERROR: {-extra} TOO MANY ALLOCATED)"
            else:
                msg = ""
            #
            print(f"Poles {ndx} = {poles[ndx]}/{inventory_poles[ndx]}  {msg}")
            bases = bases + poles[ndx]
        #

        extra = inventory_bases - bases
        if extra == 0:
            msg = "(WARNING EXACT COUNT)"
        elif extra == 1:
            msg = "(WARNING, ONLY 1 SPARE)"
        elif extra < 0:
            msg = f"(ERROR: {-extra} TOO MANY ALLOCATED)"
        else:
            msg = ""
        #
        print(f"Bases = {bases} {msg}")

    #

    #####################################################################
    #####################################################################
    def process(self):
        """ Do the whole process """

        verbose = False

        # Read in quilts and racks
        self.read_quilts()
        self.read_racks()
        self.read_overrides()

        # Information printout
        print(f"There are {len(self.quilts)} quilts and {len(self.racks)} slats")

        # First assign all overrides
        for over in self.overrides:
            self.force(over, verbose)
        #

        # Assign each quilt to a rack
        for quilt in self.quilts:
            self.assign(quilt, verbose)
        #

        # Look for quilts that were not assigned
        # TODO

        # Sort racks by row, then side, then bay, then level
        # The bay is selected as l2r or dxf
        self.racks = sorted(self.racks,
                            key=itemgetter(R_ROW, R_SIDE, self.right_bay, R_LEVEL),
                            reverse=False)

        # Now generate the DXF files for each row
        if not self.nodxf:
            self.generate_dxf()
            self.generate_plan_view()
        else:
            print("Skip DXF")
        #

        if self.show_racks:
            self.print_racks()
        #

        self.print_materials()

        self.create_quilt_list()

        self.create_row_list()

    #

    #####################################################################
    #####################################################################
    def force(self, over, verbose=False):
        """ Force quilt to rack """

        found = False

        if verbose:
            print(f"Forcing: {over[O_QID]}")

        # Get the quilt to force
        quilt = self.get_quilt_by_id(over[O_QID])
        if quilt is None:
            print(f"Warning: QuiltID {over[O_QID]} not a valid ID in Override file")
            return
        #

        fail_reason = ""

        # For each rack
        for rack in self.racks:

            if rack[R_CLASS] == 'X':
                continue

            # If the right rack
            elif (rack[R_ROW] == over[O_ROW]) and    \
                 (rack[R_SIDE] == over[O_SIDE]) and    \
                 (rack[R_RBAY] == over[O_BAY]) and    \
                 (rack[R_LEVEL] == over[O_LEVEL]):

                # This is the right spot

                # Sanity checks
                # Slats need 2 inches on each side to engage the poles
                if rack[R_SWIDTH]*12 - 4.0 < rack[R_RWIDTH]:
                    print(f"Width failure: {rack}")
                    sys.exit()
                #

                # Warning
                if quilt[Q_CLASS] != rack[R_CLASS]:
                    print("Warning: Forcing quilt %s to rack %d of different class (%s->%s)" %
                          (quilt[Q_ID], rack[R_ID], quilt[Q_CLASS], rack[R_CLASS]))
                #

                # Does quilt fit on the remaining width of this rack?
                if quilt[Q_WIDTH]+0.5*2 <= rack[R_REMAIN]:

                    # Does quilt fit in height?
                    if quilt[Q_HEIGHT] <= rack[R_HEIGHT]:

                        # If there are other quilts on this slat
                        if len(rack[R_QUILTS]) > 0:

                            # Find the size of the first quilt on this slat
                            first_quilt = self.get_quilt_by_id(rack[R_QUILTS][0])
                            if first_quilt is None:
                                print("  Opps")
                                sys.exit()
                            #

                        else:
                            if verbose:
                                print("  solo")

                        #

                        # Quilt fits
                        # print("  Quilt(%s) %7s fits on row %2s side %s bay %d level %s" % \
                        # (quilt[Q_CLASS],
                        #  quilt[Q_ID],
                        #  rack[R_ROW],
                        #  rack[R_SIDE],
                        #  rack[R_RBAY],
                        #  rack[R_LEVEL])

                        # Assign this quilt to this rack
                        rack[R_REMAIN] = rack[R_REMAIN] - \
                            quilt[Q_WIDTH] - 0.5*2
                        rack[R_QUILTS].append(quilt[Q_ID])

                        # Assign rack to quilt
                        quilt[Q_SLAT] = rack[R_ID]

                        found = True
                        break

                    else:
                        if verbose:
                            print("  Not high enough")
                        fail_reason += "Not high enough "
                    #
                else:
                    if verbose:
                        print("  Not wide enough")
                    fail_reason += "Not wide enough "
                #
            else:
                if verbose:
                    print("  Not right class", rack[R_ROW], over[O_ROW],
                          rack[R_SIDE],  over[O_SIDE],
                          rack[R_RBAY],  over[O_BAY],
                          rack[R_LEVEL], over[O_LEVEL])
                fail_reason += "Not right class "
            #
        # end racks

        if not found:
            print("Force, Not assigned: ", quilt[Q_ID], fail_reason)
        #

    #

    #####################################################################
    #####################################################################
    def assign(self, quilt, verbose):
        """ Assign quilts to racks """

        found = False

        if verbose:
            print(f"processing: {quilt[Q_ID]}")

        if self.is_quilt_forced(quilt[Q_ID]):
            print(f"Forced: {quilt[Q_ID]}")
            return

        # For each rack
        for rack in self.racks:

            if rack[R_CLASS] == 'X':
                continue

            # Sanity checks
            # Slats need 2 inches on each side to engage the poles
            if rack[R_SWIDTH]*12 - 4.0 < rack[R_RWIDTH]:
                print(f"Width failure: {rack}")
                sys.exit()

            if verbose:
                print("  Rack %d" % rack[R_ID])

            # If right class
            if quilt[Q_CLASS] == rack[R_CLASS]:

                # Does quilt fit on the remaining width of this rack?
                if quilt[Q_WIDTH]+0.5*2 <= rack[R_REMAIN]:

                    # Does quilt fit in height?
                    if quilt[Q_HEIGHT] <= rack[R_HEIGHT]:

                        # If there are other quilts on this slat
                        if len(rack[R_QUILTS]) > 0:

                            # Find the size of the first quilt on this slat
                            first_quilt = self.get_quilt_by_id(rack[R_QUILTS][0])
                            if first_quilt is None:
                                print("  Opps")
                                sys.exit()
                            #

                            heigth = first_quilt[Q_HEIGHT]
                            if heigth == 0:
                                heigth = 1

                            # Is the height of this quilt comperable to the others?
                            percent = rack[R_TOLERANCE]
                            if math.fabs(quilt[Q_HEIGHT] - heigth)/heigth > percent:
                                if verbose:
                                    print("  Not similar %d %d" %
                                          (quilt[Q_HEIGHT], heigth))
                                continue
                            #

                        else:
                            if verbose:
                                print("  solo")

                        #

                        # Quilt fits
                        if False:
                            print("  Quilt(%s) %7s fits on row %2s side %s bay %d level %s" %
                                  (quilt[Q_CLASS], quilt[Q_ID], rack[R_ROW], rack[R_SIDE],
                                   rack[R_RBAY], rack[R_LEVEL]))
                        #

                        # Assign this quilt to this rack
                        rack[R_REMAIN] = rack[R_REMAIN] - \
                            quilt[Q_WIDTH] - 0.5*2
                        rack[R_QUILTS].append(quilt[Q_ID])

                        # Assign rack to quilt
                        quilt[Q_SLAT] = rack[R_ID]

                        found = True
                        break

                    else:
                        if verbose:
                            print("  Not high enough")
                    #
                else:
                    if verbose:
                        print("  Not wide enough")
                #
            else:
                if verbose:
                    print("  Not right class")
            #
        # end racks

        if not found:
            print("Not assigned: %s (W:%d H:%d C:%s)" % (quilt[Q_ID],
                                                         quilt[Q_WIDTH], quilt[Q_HEIGHT], quilt[Q_CLASS]))
        #

    #

    #####################################################################
    #####################################################################
    def generate_dxf(self):
        """ Generate the DXF files for each row """

        print("Generating DXF files")

        # Define some constants
        gap = 1          # gap between quilt
        advance = 12*12  # Amount to advance down the page for each row
        pole_width = 2           # Poles are two inches wide
        max_text_size = 5.0     # Maximum text size

        # Set a last value that will be different on first pass
        last = self.racks[len(self.racks)-1]

        # Open the master layout of all rows
        master = dxf.drawing("./DXF/Master.dxf")

        # Where to start on the page
        x_org = 0
        y_org = advance   # Start up a bit as we drop down first before printing

        name = None

        # For each rack
        for rack in self.racks:

            # Skip if Class is X (exclude)
            if rack[R_CLASS] == 'X':
                continue

            # If we changed rows/sides
            if (rack[R_ROW] != last[R_ROW]) or (rack[R_SIDE] != last[R_SIDE]):

                # Close last file
                if name is not None:

                    # Add row Width
                    txt = "L=%d'%d\"" % (last_width/12, last_width % 12)
                    sheet.add(dxf.text(txt, (90, y_org-10), height=4.0))
                    master.add(dxf.text(txt, (90, y_org-10), height=4.0))

                    # Save the sheet
                    sheet.save()

                    del sheet
                #

                # Open new file
                name = "./DXF/Row_%d_%s.dxf" % (rack[R_ROW], rack[R_SIDE])
                sheet = dxf.drawing(name)

                # Reset sheet variables
                x_org = 0
                y_org = y_org - advance   # Advance down the page

                # Add row name
                txt = "ROW: " + str(rack[R_ROW]) + '-' + rack[R_SIDE]
                sheet.add(dxf.text(txt, (2, y_org-10), height=7.0))
                master.add(dxf.text(txt, (2, y_org-10), height=7.0))

            # Same row/side
            else:

                # If we changed bays
                if rack[self.right_bay] != last[self.right_bay]:

                    # Point to next bay's origin
                    x_org = x_org + last[R_RWIDTH] + pole_width
                #

            #

            # Get pole heights and widths
            left_pole = rack[R_LEFT] * 12
            right_pole = rack[R_RIGHT] * 12

            # Get slat height
            if rack[R_LEVEL] == 'Top':
                slat_heigth = min(left_pole, right_pole)
            elif rack[R_LEVEL] == 'Mid':
                slat_heigth = min(left_pole, right_pole) - rack[R_HEIGHT]
            else:
                print("Invalid level")
                sys.exit()
            #

            # Draw left pole
            sheet.add(dxf.rectangle((x_org, y_org), -pole_width, left_pole))
            master.add(dxf.rectangle((x_org, y_org), -pole_width, left_pole))

            # Annotate height
            txt = "%d'" % (rack[R_LEFT])
            sheet.add(dxf.text(txt, (x_org-pole_width, y_org+left_pole+2), height=4.0))
            master.add(dxf.text(txt, (x_org-pole_width, y_org+left_pole+2), height=4.0))

            # Draw right pole
            sheet.add(dxf.rectangle((x_org+rack[R_RWIDTH], y_org), pole_width,
                right_pole))
            master.add(dxf.rectangle((x_org+rack[R_RWIDTH], y_org), pole_width,
                right_pole))

            # Annotate height
            last_width = x_org+rack[R_RWIDTH]+pole_width+pole_width
            txt = "%d'" % (rack[R_RIGHT])
            sheet.add(
                dxf.text(txt, (x_org+rack[R_RWIDTH], y_org+right_pole+2), height=4.0))
            master.add(
                dxf.text(txt, (x_org+rack[R_RWIDTH], y_org+right_pole+2), height=4.0))

            # Add a gap between quilt
            x_pos = x_org + gap

            # If bay/level is empty
            if len(rack[R_QUILTS]) != 0:

                # Annotate slat length
                txt = str(rack[R_SWIDTH]) + "'"
                sheet.add(
                    dxf.text(txt, (x_org+rack[R_RWIDTH]/2, y_org+slat_heigth+2), height=4.0))
                master.add(
                    dxf.text(txt, (x_org+rack[R_RWIDTH]/2, y_org+slat_heigth+2), height=4.0))

                # For each quilt id on the rack
                for qid in rack[R_QUILTS]:

                    # Get the quilt from its ID
                    quilt = self.get_quilt_by_id(qid)

                    # Draw quilts
                    sheet.add(dxf.rectangle((x_pos, y_org+slat_heigth),
                              quilt[Q_WIDTH], -quilt[Q_HEIGHT]))
                    master.add(dxf.rectangle((x_pos, y_org+slat_heigth),
                               quilt[Q_WIDTH], -quilt[Q_HEIGHT]))

                    if quilt[Q_WIDTH] > len(quilt[Q_ID])*max_text_size:
                        ang = 0.0
                        x_txt = x_pos+2
                        y_txt = y_org+slat_heigth-7
                        text_size = max_text_size

                    else:

                        ang = 0.0
                        x_txt = x_pos+2
                        y_txt = y_org+slat_heigth-7
                        text_size = quilt[Q_WIDTH]/(len(quilt[Q_ID])+1)
                        if quilt[Q_HEIGHT] < text_size:
                            text_size = quilt[Q_HEIGHT]
                        text_size = min(text_size, max_text_size)
                    #

                    # Draw quilt text
                    txt = quilt[Q_ID]
                    sheet.add(dxf.text(txt, (x_txt, y_txt),
                              height=text_size, rotation=ang))
                    master.add(dxf.text(txt, (x_txt, y_txt),
                               height=text_size, rotation=ang))

                    # Print details on the quilt
                    if not self.nodetail:

                        txt = str(quilt[Q_WIDTH])
                        sheet.add(dxf.text(txt, (x_txt, y_txt-text_size-1),
                                  height=text_size, rotation=ang))
                        master.add(dxf.text(txt, (x_txt, y_txt-text_size-1),
                                   height=text_size, rotation=ang))

                        txt = str(quilt[Q_HEIGHT])
                        sheet.add(dxf.text(txt, (x_txt,
                            y_txt-text_size-1-text_size-1),
                                  height=text_size, rotation=ang))
                        master.add(
                            dxf.text(txt, (x_txt,
                                y_txt-text_size-1-text_size-1),
                                height=text_size, rotation=ang))

                        if self.is_quilt_forced(quilt[Q_ID]):
                            force_flag = "*"
                        else:
                            force_flag = ""
                        #
                        txt = "%d%s%d%s%s" % (
                            rack[R_ROW], rack[R_SIDE][0], rack[R_RBAY], rack[R_LEVEL][0], force_flag)
                        sheet.add(
                            dxf.text(txt, (x_txt,
                                y_txt-text_size-1-text_size-1-text_size-1),
                                height=text_size, rotation=ang))
                        master.add(
                            dxf.text(txt, (x_txt,
                                y_txt-text_size-1-text_size-1-text_size-1),
                                height=text_size, rotation=ang))
                    #

                    # Move over width of quilt plus gap
                    x_pos = x_pos + quilt[Q_WIDTH] + gap

                #

            #

            # Save last values
            last = rack

        #

        # Add row Width
        txt = "L=%d'%d\"" % (last_width/12, last_width % 12)
        sheet.add(dxf.text(txt, (90, y_org-10), height=4.0))
        master.add(dxf.text(txt, (90, y_org-10), height=4.0))

        # Save the sheet
        sheet.save()
        master.save()

    #

    #####################################################################
    #####################################################################
    def generate_plan_view(self):
        """ Generate PlanView DXF file
           This generates a DXF that can be cut and pasted into the Lion's hall
           floor plan drawing. """

        scale_factor = 1.0/12.0   # Scale factor

        print("Generating PlanView DXF file")

        # Define some constants
        advance = 150*scale_factor    # Amount to advance down the page for each row
        pole_width = 2*scale_factor   # Poles are two inches wide
        half_pole_width = (pole_width/2)          # Poles are two inches wide
        base_dia = 22.0*scale_factor
        base_rad = base_dia/2.0

        # Set a last value that will be different on first pass
        last = self.racks[len(self.racks)-1]

        # Open the PlanView file
        plan_view = dxf.drawing("./DXF/PlanView.dxf")
        plan_view.add_style("ARIAL_BOLD")

        # Where to start on the page
        x_org = 0
        y_org = advance   # Start up a bit as we drop down first before printing

        # name = None

        # For each rack
        for rack in self.racks:

            # Skip if Class is X (exclude)
            if rack[R_CLASS] == 'X':
                continue

            # If we changed rows
            if rack[R_ROW] != last[R_ROW]:

                # Reset sheet variables
                x_org = 0
                y_org = y_org - advance   # Advance down the page

                # Add row name
                txt = "%d" % rack[R_ROW]
                plan_view.add(
                    dxf.text(txt, (36*scale_factor, y_org-0*scale_factor), height=2.0))

            # Same row
            else:

                # If we changed bays
                if rack[self.right_bay] != last[self.right_bay]:

                    # Point to next bay's origin
                    x_org = x_org - (last[R_RWIDTH]*scale_factor + pole_width)
                #

            #

            if rack[R_SIDE] != last[R_SIDE]:

                # Reset sheet variables
                x_org = 0
            #

            # Draw the two poles and the line between them
            plan_view.add(dxf.rectangle((x_org-base_rad, y_org-base_rad), base_dia,
                base_dia))
            plan_view.add(dxf.rectangle(
                (x_org-rack[R_RWIDTH]*scale_factor-base_rad, y_org-base_rad), base_dia,
                base_dia))
            plan_view.add(
                dxf.line((x_org, y_org), (x_org-rack[R_RWIDTH]*scale_factor, y_org)))

            # Annotage the poles heights
            txt = "%d'" % (rack[R_LEFT])
            plan_view.add(
                dxf.text(txt, (x_org+half_pole_width, y_org+13*scale_factor), height=1.5))
            txt = "%d'" % (rack[R_RIGHT])
            plan_view.add(dxf.text(
                txt, (x_org-rack[R_RWIDTH]*scale_factor-half_pole_width, y_org+13*scale_factor), height=1.5))

            # Annotate the slat and actual widths
            txt = "%d'" % (rack[R_SWIDTH])
            if rack[R_SIDE] == "Front":
                if rack[R_LEVEL] == "Top":
                    y_off = 0.5
                else:
                    y_off = 2.0
            else:
                if rack[R_LEVEL] == "Top":
                    y_off = -1.5
                else:
                    y_off = -3.0
                #
            #
            plan_view.add(
                dxf.text(txt, (x_org-rack[R_RWIDTH]*scale_factor/2, y_org+y_off), height=1.0))

            # Save last values
            last = rack

        #

        # Save the sheet
        plan_view.save()

    #

    #####################################################################
    #####################################################################
    def get_quilt_by_id(self, qid):
        """ Get a single quilts information by its ID """
        for quilt in self.quilts:
            if quilt[Q_ID] == qid:
                return quilt
            #
        #
        return None
    #

    #####################################################################
    #####################################################################
    def is_quilt_forced(self, qid):
        """ Return True if the quilt is forced """

        for over in self.overrides:
            if over[O_QID] == qid:
                return True
        #
        return False
    #


# end of class


#####################################################################
# Main entry point
#####################################################################
if __name__ == "__main__":

    # Create a quilt object
    obj = QuiltApp()

    # Start processing
    obj.process()


# end of gile
