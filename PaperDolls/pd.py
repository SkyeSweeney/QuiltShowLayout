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
A_QID   = 7  # Quilt ID for the quilt in this area

########################################################################
# The main application class
########################################################################
class App:

    ####################################################################
    ####################################################################
    def __init__(self):
        """  Constructor """

        # Check for arguments
        if len(sys.argv) != 2:
            print("Usage: pd.py fn.csv")
            exit(1)
        #

        # Get the file name of the csv file
        fn = sys.argv[1]

        self.page_w = 8.5
        self.page_h = 11.0

        # Border on edge of physical paper
        self.border = 0.25

        # Size of the writeable paper
        self.page_w = -self.border + self.page_w - self.border
        self.page_h = -self.border + self.page_h - self.border

        # Set verbose flag for more output
        self.verbose = False

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
        area = [self.last_aid, self.i_page, x, y, self.page_w, self.page_h, used, cid, qid]
        self.areas.append(area)


        self.assigned = []

        #############################
        # Read in quilts into list
        #############################
        max_h = 0
        max_w = 0
        self.quilts = []
        fp = open(fn, "r")
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
            if w > max_w:
                max_w = w
            if h > max_h:
                max_h = h
        #
        fp.close()

        # Sort the quilts by reducing size
        self.quilts.sort(reverse=True,key=self.computeArea)

        ###############
        # Compute scale
        ###############
        ar = self.page_w / self.page_h  # Aspect ratio
        z = ar * max_h
        if z > max_w:
            self.scale = self.page_h / max_h
        else:
            self.scale = self.page_w / max_w
        #
        self.scale = self.scale / 2.0
        self.scale = 1/12
        print(f"Max width {max_w}, max heigth {max_h}, Scale 1: {1/self.scale}")

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
            q_x    = float(quilt[Q_WIDTH])  * self.scale  # Put into paper space
            q_y    = float(quilt[Q_HEIGHT]) * self.scale  # Put into paper space

            if self.verbose:
                print(f"Trying to place {qid} of size ({quilt[Q_WIDTH]:.1f}*{quilt[Q_HEIGHT]:.1f}) paper size ({q_x:.1f}*{q_y:.1f})")
            #

            # Try to place quilt in any of the unused areas
            placed = self.place(qid, quilt)

            # If we could not place in current unused areas
            if not placed: 

                if self.verbose:
                    print("  Unable to place. Starting new page")

                # Create a new page
                self.i_page += 1
                self.last_aid += 1
                x = 0
                y = 0
                cid = "?"
                qid = "?"
                used = False
                area = [self.last_aid, self.i_page, x, y, self.page_w, self.page_h, used, cid, qid]
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
        q_x    = float(quilt[Q_WIDTH])  * self.scale  # Put into paper space
        q_y    = float(quilt[Q_HEIGHT]) * self.scale  # Put into paper space

        # For each area
        for area in self.areas:

            page  = area[A_PAGE]
            a_x   = area[A_X] # Origin of area on page
            a_y   = area[A_Y] # Orrgin of area on page
            a_w   = area[A_W] # Width of area
            a_h   = area[A_H] # Height of area
            used  = area[A_USED] # Area used
            aid   = area[A_AID]  # Id fo area

            if self.verbose:
                print(f"  Look at area aid:{aid} p:{page} x:{a_x:.1f} y:{a_y:.1f} w:{a_w:.1f} h:{a_h:.1f} u:{used}")
            #

            # If this area is in use, skip
            if used:
                if self.verbose:
                    print(f"  Used")
                continue
            #

            # If the quilt fits in this area
            if (q_y < a_h) and (q_x < a_w):

                if self.verbose:
                    print(f"  Placing quilt {qid} in aid:{aid} p:{page} x:{a_x:.1f} y:{a_y:.1f} w:{a_w:.1f} h:{a_h:.1f} u:{used}")

                # Update the area information
                area[A_QID]  = qid
                area[A_USED] = True

                # Add area to the Assigned list
                self.assigned.append(area)

                # Set flag to indicate we placed with quilt
                placed = True

                # Determine left over area1 to right
                r = a_w - 0.25 - q_x
                if r > 0:
                    x = a_x + q_x + 0.25
                    y = a_y
                    w = a_w - 0.25 - q_x
                    h = q_y
                    used = False
                    cid = "?"
                    qid = "?"
                    self.last_aid += 1
                    area1 = [self.last_aid, page, x, y, w, h, used, cid, qid]
                    self.areas.append(area1)
                    if self.verbose:
                        print(f"  Adding area1 aid:{self.last_aid} p:{page} x:{x:.1f} y:{y:.1f} w:{w:.1f} h:{h:.1f} u:False")
                    #
                else:
                    if self.verbose:
                        print(f"  No room to right")
                #

                # Determine left over area2 above
                r = a_h - 0.25 - q_y
                if r > 0:
                    self.last_aid += 1
                    x = a_x
                    y = a_y + q_y + 0.25
                    w = a_w
                    h = a_h - 0.25 - q_y
                    used = False
                    cid = "?"
                    qid = "?"
                    area2 = [self.last_aid, page, x, y, w, h, used, cid, qid]
                    self.areas.append(area2)
                    if self.verbose:
                        print(f"  Adding area2 aid:{self.last_aid} p:{page} x:{x:.1f} y:{y:.1f} w:{w:.1f} h:{h:.1f} u:False")
                    #
                else:
                    if self.verbose:
                        print(f"  No room above")
                #

                # Quit loop if we placed the quilt in a area
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

            # Set origin for this PAGE
            x_page_org = 5.0
            y_page_org = 5.0 + a[A_PAGE] * self.page_h * 2

            # If a new page
            if a[A_PAGE] != last_page:
                # Draw page border
                r = dxf.rectangle((x_page_org, y_page_org) , self.page_w, self.page_h)
                pd.add(r)
            #

            # Find the quilt given its id
            q = self.find_quilt(a[A_QID])
            #if self.verbose:
            #    print(f"id:{qid(a)}, p:{page(a)}, x:{xOrg:.1f}, y:{yOrg:.1f}, w:{q[Q_WIDTH]*self.scale:.1f}, h:{q[Q_HEIGHT]*self.scale:.1f}")

            # Get the origin of the quilt
            x_quilt_org = x_page_org + a[A_X]
            y_quilt_org = y_page_org + a[A_Y]

            # Add in rectangle for the quilt outline
            r = dxf.rectangle((x_quilt_org, y_quilt_org) , q[Q_WIDTH]*self.scale, q[Q_HEIGHT]*self.scale)
            pd.add(r)

            # Compute the origin of the text
            t = q[Q_WIDTH] / 10.0 * self.scale
            x_text = x_quilt_org 
            y_text = y_quilt_org + q[Q_HEIGHT]*self.scale - t

            # Add in QID/Class
            s = f"{q[Q_QID]}({q[Q_CLASS]})"
            pd.add(dxf.text(s, (x_text, y_text), height = t))

            x_text = x_quilt_org
            y_text = y_quilt_org + q[Q_HEIGHT]*self.scale - t*2

            # Add in size
            s = f"({q[Q_WIDTH]:.1f} * {q[Q_HEIGHT]:.1f})"
            t = q[Q_WIDTH] / 10.0 * self.scale
            pd.add(dxf.text(s, (x_text, y_text), height = t))


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



