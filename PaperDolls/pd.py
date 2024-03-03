#!/usr/bin/python3


import sys
import math
import os
from dxfwrite import DXFEngine as dxf




Q_CLASS  = 0
Q_W      = 1
Q_H      = 2
Q_NOTES  = 3
Q_PLACED = 4

A_PAGE = 0
A_X = 1
A_Y = 2
A_W = 3
A_H = 4
A_USED = 5

class App:

    ####################################################################
    # Constructor
    ####################################################################
    def __init__(self):

        self.pageW = 8.5 - 0.5
        self.pageH = 11.0 - 0.5

        self.verbose = True


        self.iPage = 1
        
        self.areas = []
        self.areas.append([self.iPage, 0.0, 0.0, self.pageW, self.pageH, False])


        self.assigned = []

        # Read in qs
        maxH = 0
        maxW = 0
        self.qs = {}
        fp = open("Quilts.csv", "r")
        for line in fp:
            toks   = line.strip().split(",")
            qid    = toks[0]
            cid    = toks[1]
            w      = float(toks[2])
            h      = float(toks[3])
            notes  = toks[4]
            placed = False
            
            # Add to dictionary
            self.qs[qid] = [cid,w,h,notes,placed]

            # Keep track of largest q W and H
            if w > maxW:
                maxW = w
            if h > maxH:
                maxH = h
        #    
        fp.close()

        # Compute scale
        ar = 8.5 / 11.0
        z = ar * maxH
        if z > maxW:
            self.scale = 11.0 / maxH
        else:
            self.scale = 8.5 / maxW 
        #    
        self.scale = self.scale / 2.0
        print(maxW, maxH, self.scale)

        self.printQs()

    #

    ####################################################################
    # Print areas
    ####################################################################
    def printAreas(self):
        print("********** Areas *************")
        for a in self.areas:
            print(a)
        #
        print("******************************")
    #    

    ####################################################################
    # Print qs
    ####################################################################
    def printQs(self):
        print("*********** QS ***************")
        for key, value in self.qs.items():
            print(key, value)
        #
        print("******************************")
    #    

    ####################################################################
    # Start the process
    ####################################################################
    def run(self):

        # For each q
        for qid, value in self.qs.items():

            cid = value[0]
            qx  = float(value[1]) * self.scale
            qy  = float(value[2]) * self.scale
            notes = value[3]
            placed = value[4]

            if self.verbose:
                print("Trying to place %s of size (%f %f)" % (qid, qx, qy))

            # Try to place Q in an area
            Placed = self.place(qid, value)

            # If we could not place in current areas, create a new page
            if not Placed:

                self.iPage += 1
                self.areas.append([self.iPage, 
                                   0.0, 
                                   0.0, 
                                   self.pageW, 
                                   self.pageH, 
                                   False])

                # Place on the new page                    
                Placed = self.place(qid, value)
                if not Placed:
                    print("Error")
                    sys.exit(1)
                #    


        # For each q

        if self.verbose:
          print("Qs placed. Now generating DXF")


        self.createDxf()

    #


    ####################################################################
    # Place a Q into an area
    ####################################################################
    def place(self, qid, value):

        Placed = False

        cid    = value[0]
        qx     = float(value[1]) * self.scale
        qy     = float(value[2]) * self.scale
        notes  = value[3]
        placed = value[4]

        # For each area
        for area in self.areas:

            page = area[A_PAGE]
            ax   = area[A_X]
            ay   = area[A_Y]
            aw   = area[A_W]
            ah   = area[A_H]
            used = area[A_USED]

            # If this area is in use, skip
            if used:
                continue
            #    

            if self.verbose:
                print("  In area p:%d x:%.1f y:%.1f w:%.1f h:%.1f u:%d" % (page,ax,ay,aw,ah, used))

            # Fit in current area?
            if (qy < ah) and (qx < aw):

                if self.verbose:
                    print("  Placing q in area p:%d x:%.1f y:%.1f w:%.1f h:%.1f u:%d" % (page,ax,ay,aw,ah,used))

                # Add to the assigned list
                self.assigned.append([qid, area])
                Placed = True

                # Mark Q as placed
                value[4] = True

                # Mark Area as used
                area[A_USED] = True

                # Determine area1
                x = ax + qx + 0.5
                y = ay
                w = aw-x
                h = qy
                area1 = [page, x, y, w, h, False]
                if w > 0:
                    if self.verbose:
                        print("  Adding area1 p:%d x:%.1f y:%.1f w:%.1f h:%.1f u:%d"% \
                        (page,x,y,w,h, False))
                    self.areas.append(area1)
                #    

                # Determine area2
                x = ax
                y = ay + qy + 0.5
                w = aw
                h = ah - y
                area2 = [page, x, y, w, h, False]
                if h > 0:
                    if self.verbose:
                        print("  Adding area2 p:%d x:%.1f y:%.1f w:%.1f h:%.1f u:%d"% \
                        (page,x,y,w,h, False))
                    self.areas.append(area2)
                #    

                break

            # If it fit

        # For each area     

        return Placed
    #

    ####################################################################
    # Create the DXF file
    ####################################################################
    def createDxf(self):

        # Sort function; returns page number
        def page(e):
            return(e[1][0])
        #    
        def xPos(e):
            return(e[1][1])
        #    
        def yPos(e):
            return(e[1][2])
        #    
        def w(e):
            return(e[1][3])
        #    
        def h(e):
            return(e[1][4])
        #    
        def qid(e):
            return(e[0])
        #    

        lastPage = -10

        # Open the master layout of all rows
        pd = dxf.drawing("PD.dxf")

        # Sort the assinged list by page number
        self.assigned.sort(key=page)

        # For each assignment
        for a in self.assigned:

            # Set origin for this page
            xOrg = xPos(a)
            yOrg = page(a) * self.pageH * 2 + yPos(a)

            # If a new page
            if page(a) != lastPage:
                r = dxf.rectangle((xOrg, yOrg) , 8.5, 11.0)
                pd.add(r)
            #    

            q = self.qs[qid(a)]
            if self.verbose:
                print(qid(a), page(a), xOrg, yOrg,  q[Q_W]*self.scale, q[Q_H]*self.scale)

            # Add in rectangle
            r = dxf.rectangle((xOrg, yOrg) , q[Q_W]*self.scale, q[Q_H]*self.scale)
            pd.add(r)

            # Add in QID/Class
            s = "%s(%s)" % (qid(a), "XXX")
            t = q[Q_W] / 10.0 * self.scale
            pd.add(dxf.text(s, (xOrg, yOrg+q[Q_H]*self.scale - t), height = t))

            # Add in size
            s = "(%.1f * %.1f)" % (q[Q_W], q[Q_H])
            t = q[Q_W] / 10.0 * self.scale
            pd.add(dxf.text(s, (xOrg, yOrg+q[Q_H]*self.scale - t*2), height = t))


            lastPage = page(a)

        #


        pd.save()

    #    
#



if __name__ == "__main__":

    obj = App()
    obj.run()



