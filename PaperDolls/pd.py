#!/usr/bin/python3

########################################################################
# Program to print all the quilts to paper.
# This would allow you to layout a show in a very manual way
########################################################################

import sys
from dxfwrite import DXFEngine as dxf




# Column indices for the Quilts.csv file
CSV_QID       = 0
CSV_CLASS     = 1
CSV_WIDTH     = 2
CSV_HEIGHT    = 3

# Column indices for the Quilt list
Q_QID       = 0
Q_CLASS     = 1
Q_WIDTH     = 2
Q_HEIGHT    = 3

# Array indices for the Areais and Assigned lists
A_AID   = 0  # Id of this area
A_PAGE  = 1  # Page number
A_X     = 2  # X Location of quilt on page
A_Y     = 3  # Y location of quilt on page
A_W     = 4  # Width of quilt on page
A_H     = 5  # Length/height of quilt on page
A_USED  = 6  # Area assiged
A_CLASS = 7  # Class for the quilt in this area
A_QID   = 8  # Quilt ID for the quilt in this area

########################################################################
# The main application class
########################################################################
class App:

    ####################################################################
    ####################################################################
    def __init__(self):
        """  Constructor """

        self.page_w = 8.5
        self.page_h = 11.0

        # Border on edge of physical paper
        self.border = 0.25

        # Size of the writeable paper
        self.pageW = -self.border + self.page_w - self.border
        self.pageH = -self.border + self.page_h - self.border

        # Set verbose flag for more output
        self.verbose = True

        # Start at page one
        self.i_page = 1

        # Start with the first node in the Areas lists
        self.areas = []
        self.last_aid = 0
        x = 0
        y = 0
        cid = "?"
        qid = "?"
        used = False
        area = [self.last_aid, self.i_page, x, y, self.pageW, self.pageH, used, cid, qid]
        self.areas.append(area)


        self.assigned = []

        #############################
        # Read in quilts into list
        #############################
        maxH = 0
        maxW = 0
        self.quilts = []
        fp = open("Quilts.csv", "r")
        for line in fp:

            # Tokenize the line
            toks   = line.strip().split(",")

            # Skip comments
            if toks[0][0] == "#":
                continue

            # Pull out fields
            qid    = toks[CSV_QID]
            cid    = toks[CSV_CLASS]
            w      = float(toks[CSV_WIDTH])
            h      = float(toks[CSV_HEIGHT])
            placed = False

            # Add to dictionary using quilt ID as key
            q = [qid, cid, w, h, placed]
            #print(f"Appending {q}")
            self.quilts.append(q)

            # Keep track of largest quilt W and H
            if w > maxW:
                maxW = w
            if h > maxH:
                maxH = h
        #
        fp.close()

        # Sort the quilts by reducing size
        self.quilts.sort(reverse=True,key=self.computeArea)

        ###############
        # Compute scale
        ###############
        ar = self.page_w / self.page_h  # Aspect ratio
        z = ar * maxH
        if z > maxW:
            self.scale = self.page_h / maxH
        else:
            self.scale = self.page_w / maxW
        #
        self.scale = self.scale / 2.0
        print(f"Max width {maxW}, max heigth {maxH}, Scale {self.scale}")

        self.print_quilts()

    #

    ####################################################################
    ####################################################################
    def computeArea(self, quilt):
        """  Compute the area of a quilt """
        a = quilt[Q_WIDTH] * quilt[Q_HEIGHT]
        return a
    #

    ####################################################################
    ####################################################################
    def printAreas(self):
        """ Print areas """
        print("********** Areas *************")
        for area in self.areas:
            print(f"Areas:{area}")
        #
        print("******************************")
    #

    ####################################################################
    ####################################################################
    def print_quilts(self):
        """ Print Quilts list """
        print("*********** Quilts ***********")
        for quilt in self.quilts:
            self.print_quilt(quilt)
        #
        print("******************************")
    #

    ####################################################################
    ####################################################################
    def print_quilt(self, quilt):
        """ Print Quilt """
        print(f"qid:{quilt[Q_QID]} cid:{quilt[Q_CLASS]} w:{quilt[Q_WIDTH]:.1f} h:{quilt[Q_HEIGHT]:.1f}")
    #

    ####################################################################
    ####################################################################
    def run(self):
        """ Start the process """

        # For each quilt
        for quilt in self.quilts:

            qid    = quilt[Q_QID]
            cid    = quilt[Q_CLASS]
            qx     = float(quilt[Q_WIDTH])  * self.scale  # Put into paper space
            qy     = float(quilt[Q_HEIGHT]) * self.scale  # Put into paper space

            if self.verbose:
                print(f"Trying to place {qid} of size ({quilt[Q_WIDTH]:.1f}*{quilt[Q_HEIGHT]:.1f}) paper size ({qx:.1f}*{qy:.1f})")
            #

            # Try to place quilt in any of the unused areas
            placed = self.place(qid, quilt)

            # If we could not place in current unused areas
            if not placed: 

                print("  Unable to place. Starting new page")

                # Create a new page
                self.i_page += 1
                self.last_aid += 1
                x = 0
                y = 0
                cid = "?"
                qid = "?"
                used = False
                area = [self.last_aid, self.i_page, x, y, self.pageW, self.pageH, used, cid, qid]
                self.areas.append(area)

                # Place on the new page
                placed = self.place(qid, quilt)

                # Can't place a quilt on a new blank page!
                if not placed:
                    print("  Can't place quilt on new page")
                    sys.exit(1)
                #

            # Could not place

        # For each q

        if self.verbose:
            print("Quilts placed on pages. Now generating DXF")


        self.create_dxf()

    #


    ####################################################################
    ####################################################################
    def place(self, qid, quilt):
        """ Place a Quilt into an area """

        # Assume we will not be able to place the quilt
        placed = False

        # Extract fields from quilts list
        qid    = quilt[Q_QID]
        cid    = quilt[Q_CLASS]
        qx     = float(quilt[Q_WIDTH])  * self.scale  # Put into paper space
        qy     = float(quilt[Q_HEIGHT]) * self.scale  # Put into paper space

        # For each area
        for area in self.areas:

            page = area[A_PAGE]
            ax   = area[A_X]
            ay   = area[A_Y]
            aw   = area[A_W]
            ah   = area[A_H]
            used = area[A_USED]
            aid  = area[A_AID]
            cid  = area[A_CLASS]

            # If this area is in use, skip
            if used:
                continue
            #

            if self.verbose:
                print(f"  Look at area id:{aid} p:{page} x:{ax:.1f} y:{ay:.1f} w:{aw:.1f} h:{ah:.1f} u:{used}")
            #

            # If the quilt fits in this area
            if (qy < ah) and (qx < aw):

                if self.verbose:
                    print(f"  Placing quilt {qid} in aid:{aid} p:{page} x:{ax:.1f} y:{ay:.1f} w:{aw:.1f} h:{ah:.1f} u:{used}")

                # Update the area information
                area[A_QID]   = qid
                area[A_CLASS] = cid
                area[A_USED] = True

                # Add to the assigned list
                self.assigned.append(area)

                # Set flag to indicate we placed with quilt
                placed = True

                # Determine left over area1
                self.last_aid += 1
                x = ax + qx + 0.5
                y = ay
                w = aw-x
                h = qy
                used = False
                cid = "?"
                qid = "?"
                area1 = [self.last_aid, page, x, y, w, h, used, cid, qid]
                if w > 0:
                    if self.verbose:
                        print(f"  Adding area1 aid:{self.last_aid} p:{page} x:{x:.1f} y:{y:.1f} w:{w:.1f} h:{h:.1f} u:False")
                    self.areas.append(area1)
                #

                # Determine left over area2
                self.last_aid += 1
                x = ax
                y = ay + qy + 0.5
                w = aw
                h = ah - y
                used = False
                cid = "?"
                qid = "?"
                area2 = [self.last_aid, page, x, y, w, h, used, cid, qid]
                if h > 0:
                    if self.verbose:
                        print(f"  Adding area2 aid:{self.last_aid} p:{page} x:{x:.1f} y:{y:.1f} w:{w:.1f} h:{h:.1f} u:False")
                    self.areas.append(area2)
                #

                break

            # If it fit

        # For each area

        return placed
    #

    ####################################################################
    ####################################################################
    def create_dxf(self):
        """ Create the DXF file """

        # Sort function; returns page number
        def page(e):
            return(e[A_PAGE])
        #

        last_page = -10

        # Open the master layout of all rows
        pd = dxf.drawing("output.dxf")

        # Sort the assigned list by page number
        self.assigned.sort(key=page)

        # For each assignment
        for a in self.assigned:

            # Set origin for this page
            xOrg = 0
            yOrg = a[A_PAGE] * self.pageH * 2 + a[A_Y]

            # If a new page
            if a[A_PAGE] != last_page:
                r = dxf.rectangle((xOrg, yOrg) , self.page_w, self.page_h)
                pd.add(r)
            #

            q = self.find_quilt(a[A_QID])
            #if self.verbose:
            #    print(f"id:{qid(a)}, p:{page(a)}, x:{xOrg:.1f}, y:{yOrg:.1f}, w:{q[Q_WIDTH]*self.scale:.1f}, h:{q[Q_HEIGHT]*self.scale:.1f}")

            # Add in rectangle
            r = dxf.rectangle((xOrg, yOrg) , q[Q_WIDTH]*self.scale, q[Q_HEIGHT]*self.scale)
            pd.add(r)

            # Add in QID/Class
            s = f"{a[A_QID]}({a[A_CLASS]})"
            t = q[Q_WIDTH] / 10.0 * self.scale
            pd.add(dxf.text(s, (xOrg, yOrg+q[Q_HEIGHT]*self.scale - t), height = t))

            # Add in size
            s = f"({q[Q_WIDTH]:.1f} * {q[Q_HEIGHT]:.1f})"
            t = q[Q_WIDTH] / 10.0 * self.scale
            pd.add(dxf.text(s, (xOrg, yOrg+q[Q_HEIGHT]*self.scale - t*2), height = t))


            last_page = page(a)

        #


        pd.save()

    #


    ####################################################################
    ####################################################################
    def find_quilt(self, qid):
        """ Return a quilt given its ID """
        for quilt in self.quilts:
            if quilt[Q_QID] == qid:
                return quilt
            #
        #
        print(f"Unable to find quit {qid}")
        return None
    #
#



if __name__ == "__main__":

    obj = App()
    obj.run()



