#! /usr/bin/python

import sys
import math
import os
import dxfwrite
import argparse
from dxfwrite import DXFEngine as dxf
from operator import itemgetter

# Columns in the QUILT CSV file
Q_ID        = 0
Q_CLASS     = 1
Q_WIDTH     = 2
Q_HEIGHT    = 3
Q_SLAT      = 4  # Synthetic

# Columns in the RACKS CSV file
R_ID        = 0
R_ROW       = 1
R_SIDE      = 2
R_RBAY      = 3
R_DXFBAY    = 4
R_LEVEL     = 5
R_SWIDTH    = 6   # Slat width used for bay
R_RWIDTH    = 7   # Real width between poles
R_HEIGHT    = 8
R_LEFT      = 9
R_RIGHT     = 10
R_CLASS     = 11
R_TOLERANCE = 12
R_REMAIN    = 13  # Synthetic
R_QUILTS    = 14  # Synthetic

# Columns in the Overrides file
O_QID       = 0
O_ROW       = 1
O_SIDE      = 2
O_BAY       = 3
O_LEVEL     = 4


class Q():

  def __init__(self):

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
                        dest='showRack',  
                        default=False, 
                        help="Print rack info")

    stuff = parser.parse_args()
    self.nodetail    = stuff.nodetail    # Print more detail on each quilt
    self.leftToRight = stuff.l2r
    self.nodxf       = stuff.nodxf
    self.showRack    = stuff.showRack



    self.quilts     = []
    self.racks      = []
    self.overrides  = []

    if (not self.leftToRight):
        self.R_BAY = R_DXFBAY   # Print back to back
        print("Printing back to back")
    else:
        self.R_BAY = R_RBAY     # Print for printed labels
        print("Printing left to right")
    #
  #

  #####################################################################
  # Read in quilt information
  #####################################################################
  def ReadQuilts(self):

    ###########################
    # Read in quilt information
    ###########################
    print("Reading in Quilts")
    fQuilts = open("Quilts.csv", "r")


    # Read off header
    line = fQuilts.readline().strip()

    lineNum = 1
    while (True):

      line = fQuilts.readline()
      if (line == ""): break

      toks = line.strip().split(",")
      if (toks[0] == ""): continue

      # Allow for commenting out a quilt
      if (toks[0][0:1] == '#'): 
          print("Quilt %s commented out" % toks[0])
          continue
      #

      try:
        self.quilts.append( [toks[Q_ID], 
                             toks[Q_CLASS], 
                             float(toks[Q_WIDTH]), 
                             float(toks[Q_HEIGHT]), 
                             0] )  # Slat
      except:
        print("Error on Quilts line %d" % lineNum)
      #
      lineNum = lineNum + 1
    #
    fQuilts.close()
  #

  #####################################################################
  # Read in rack information
  #####################################################################
  def ReadRacks(self):

    print("Reading in racks")
    fRacks  = open("Racks.csv", "r")

    # Read off header
    line = fRacks.readline().strip()

    lineNum = 0
    while (True):

      lineNum = lineNum + 1

      line = fRacks.readline()
      if (line == ""): break

      toks  = line.strip().split(",")
      if (toks[0] == ""): continue

      if (toks[0] == "#"): continue

      assignedQuilts = []

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
                assignedQuilts]          # Assigned quilts to rack
               
        self.racks.append(rack)

      except:
        print("Error: Conversion error in Racks line %d" % lineNum)
        sys.exit(1)
      #

      # Sanity check items
      if (rack[R_SIDE] != 'Front') and (rack[R_SIDE] != 'Back'):
        print("Error: Bad side name in Racks line %d" % lineNum)
        sys.exit(1)
      #

      if (rack[R_LEVEL] != 'Top') and (rack[R_LEVEL] != 'Mid'):
        print("Error: Bad level name in Racks line %d" % lineNum)
        sys.exit()
      #

    #
    fRacks.close()
  #

  #####################################################################
  # Read in override information
  #####################################################################
  def ReadOverride(self):

    print("Reading in overrides")
    fOver  = open("Overrides.csv", "r")

    # Read off header
    line = fOver.readline().strip()

    lineNum = 1
    while (True):

      line = fOver.readline()
      if (line == ""): break

      toks  = line.strip().split(",")
      if (toks[0] == ""): continue

      try:
        over = [toks[O_QID],
                int(toks[O_ROW]), 
                toks[O_SIDE], 
                int(toks[O_BAY]), 
                toks[O_LEVEL]]
               
        self.overrides.append(over)

      except:
        print("Error: Conversion error in Overrides line %d" % lineNum)
        sys.exit(1)
      #

      # Sanity check items
      if (over[O_SIDE] != 'Front') and (over[O_SIDE] != 'Back'):
        print("Error: Bad side name in Overrides line %d" % lineNum)
        sys.exit(1)
      #

      if (over[O_LEVEL] != 'Top') and (over[O_LEVEL] != 'Mid'):
        print("Error: Bad level name in Overrides line %d" % lineNum)
        sys.exit()
      #

      lineNum = lineNum + 1
    #
    fOver.close()
  #




  #####################################################################
  #  Create the Quilt list
  #  CSV with the following format:
  #    Quilt, row, side, bay, level
  #####################################################################
  def CreateQuiltList(self):


    print("Generating QuiltList.csv")

    fp = open("QuiltList.csv", "w")

    fp.write("Quilt, Row, Side, Bay, Level\n")

    temp = []

    # Create list
    for rack in self.racks:
      for qid in rack[R_QUILTS]:
        temp.append( (qid, rack[R_ROW], rack[R_SIDE], rack[self.R_BAY], rack[R_LEVEL]) )
      #
    #

    # Sort list by qid (the zeroth element of the temp tupple)
    temp = sorted(temp, key=itemgetter(0))

    # Print list
    for i in temp:
      s = "%s, %d, %s, %d, %s" % ( i[0], i[1], i[2], i[3], i[4])
      fp.write(s+'\n')
    #

    fp.close()

  #

  #####################################################################
  #  Create the Row list
  #  CSV with the following format:
  #    row, side, bay, level, quilt
  #####################################################################
  def CreateRowList(self):


    print("Generating RowList.csv")

    fp = open("RowList.csv", "w")

    fp.write("Row, Side, Bay, Level, Quilt\n")

    temp = []

    # Create list
    for rack in self.racks:
      for qid in rack[R_QUILTS]:
        temp.append( (qid, rack[R_ROW], rack[R_SIDE], rack[self.R_BAY], rack[R_LEVEL]) )
      #
    #

    # Sort list first by qid, then by row, then side, and then by bay
    temp = sorted(temp, key=itemgetter(1,2,3,4))

    # Print list
    for i in temp:
      s = "%d, %s, %d, %s, %s"% ( i[1], i[2], i[3], i[4], i[0])
      fp.write(s+'\n')
    #

    fp.close()

  #



  #####################################################################
  #  Print racks
  #####################################################################
  def PrintRacks(self):

    for rack in self.racks:

      if (rack[R_CLASS] == 'X'): continue

      s = "%2d %2d %1s %d %1s %2d %3d %2d %2d %3s %6.2f" % \
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

      for q in rack[R_QUILTS]:
        s = s + " " + q
      #
      print(s)

    #
  #

  #####################################################################
  #  Print Materials
  #####################################################################
  def PrintMaterials(self):

    slats = {}
    slats[6]  = 0
    slats[7]  = 0
    slats[8]  = 0
    slats[9]  = 0
    slats[10] = 0
    slats[12] = 0

    Islats = {}
    Islats[6]  = 39
    Islats[7]  = 3
    Islats[8]  = 85
    Islats[9]  = 10
    Islats[10] = 34
    Islats[12] = 13

    # Actual
    poles = {}
    poles[3]  = 0
    poles[6]  = 0
    poles[7]  = 0
    poles[8]  = 0
    poles[9]  = 0
    poles[10] = 0
    poles[11] = 0

    # Inventory
    Ipoles = {}
    Ipoles[3]  = 100
    Ipoles[6]  = 4
    Ipoles[7]  = 19
    Ipoles[8]  = 40
    Ipoles[9]  = 25
    Ipoles[10] = 3
    Ipoles[11] = 100

    Ibases = 83


    print("")
    print("Bill of materials:")

    # Set a last value that will be different on first pass
    last = self.racks[len(self.racks)-1]


    # For each rack
    for rack in self.racks:

      # Skip if the 'X' (deleted) class
      if (rack[R_CLASS] == 'X'): continue

      # If we changed row/side
      if (rack[R_ROW] != last[R_ROW]) or \
         (rack[R_SIDE] != last[R_SIDE]):

        # Add left pole
        if (rack[R_SIDE] == 'Front'): poles[rack[R_LEFT]] = poles[rack[R_LEFT]] + 1

        # Add right pole
        if (rack[R_SIDE] == 'Front'): poles[rack[R_RIGHT]] = poles[rack[R_RIGHT]] + 1

        # Add slat
        slats[rack[R_SWIDTH]] = slats[rack[R_SWIDTH]] + 1

      # Same row/side
      else:

        # If we changed bays
        if (rack[self.R_BAY] != last[self.R_BAY]):

          # Add right pole
          if (rack[R_SIDE] == 'Front'): 
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

    for s in slats.keys():
      extra = Islats[s] - slats[s]
      if (extra == 0):
        msg = "(WARNING EXACT COUNT)"
      elif (extra == 1):
        msg = "(CAUTION, ONLY 1 SPARE)"
      elif (extra < 0):
        msg = "(ERROR: %d TOO MANY ALLOCATED)"%(-extra)
      else:
        msg = ""
      #
      print("Slat %d = %d/%d %s" % (s, slats[s], Islats[s],msg))
    #

    bases = 0
    for s in poles.keys():
      extra = Ipoles[s] - poles[s]
      if (extra == 0):
        msg = "(WARNING EXACT COUNT)"
      elif (extra == 1):
        msg = "(CAUTION, ONLY 1 SPARE)"
      elif (extra < 0):
        msg = "(ERROR: %d TOO MANY ALLOCATED)"%(-extra)
      else:
        msg = ""
      #
      print("Poles %d = %d/%d  %s" % (s, poles[s], Ipoles[s], msg))
      bases = bases + poles[s]
    #

    extra = Ibases - bases
    if (extra == 0):
      msg = "(WARNING EXACT COUNT)"
    elif (extra == 1):
      msg = "(WARNING, ONLY 1 SPARE)"
    elif (extra < 0):
      msg = "(ERROR: %d TOO MANY ALLOCATED)"%(-extra)
    else:
      msg = ""
    #
    print("Bases = %d %s" % (bases,msg))

  #


  #####################################################################
  # Do the whole process
  #####################################################################
  def Process(self):

    Verbose = False

    # Read in quilts and racks
    self.ReadQuilts()
    self.ReadRacks()
    self.ReadOverride()


    # Information printout
    print("There are %d quilts and %d slats" % (len(self.quilts),
        len(self.racks)))

    # First assign all overrides
    for over in self.overrides:
      self.Force(over, Verbose)
    #
    

    # Assign each quilt to a rack
    for quilt in self.quilts:
      self.Assign(quilt, Verbose)
    #

    # Look for quilts that were not assigned

    # Sort racks by row, then side, then bay, then level
    # The bay is selected as l2r or dxf
    self.racks = sorted(self.racks, 
                        key=itemgetter(R_ROW, R_SIDE, self.R_BAY, R_LEVEL), 
                        reverse=False)

    # Now generate the DXF files for each row
    if (not self.nodxf):
      self.GenerateDxf()
      self.GeneratePlanView()
    else:
        print("Skip DXF")
    #

    if (self.showRack):
      self.PrintRacks()
    #

    self.PrintMaterials()

    self.CreateQuiltList()

    self.CreateRowList()

  #


  #####################################################################
  # Force quilt to rack
  #####################################################################
  def Force(self, over, verbose=False):

    found = False


    if verbose: print("Forcing: %s, " % over[O_QID])
    
    # Get the quilt to force
    quilt = self.GetQuiltById(over[O_QID])
    if (quilt == None):
        print("Warning: QuiltID ", over[O_QID], " not a valid ID in Override file")
        return
    #
        
    failReason = ""

    # For each rack
    for rack in self.racks:

      if (rack[R_CLASS] == 'X'): 
        continue

      # If the right rack
      elif (rack[R_ROW]   == over[O_ROW]) and    \
           (rack[R_SIDE]  == over[O_SIDE]) and    \
           (rack[R_RBAY]  == over[O_BAY]) and    \
           (rack[R_LEVEL] == over[O_LEVEL]) :
           
        # This is the right spot   

        # Sanity checks
        if (rack[R_SWIDTH]*12 - 4.0 < rack[R_RWIDTH]):   # Slats need 2 inches on each side to engage the poles
          print("Width failure:", rack)
          sys.exit()
        #

        # Warning
        if quilt[Q_CLASS] != rack[R_CLASS]: 
          print("Warning: Forcing quilt %s to rack %d of different class (%s->%s)" % \
              (quilt[Q_ID], rack[R_ID], quilt[Q_CLASS], rack[R_CLASS]))
        #

        # Does quilt fit on the remaining width of this rack?
        if (quilt[Q_WIDTH]+0.5*2 <= rack[R_REMAIN]):

          # Does quilt fit in height?
          if (quilt[Q_HEIGHT] <= rack[R_HEIGHT]):

            # If there are other quilts on this slat
            if (len(rack[R_QUILTS]) > 0):

              # Find the size of the first quilt on this slat
              q = self.GetQuiltById(rack[R_QUILTS][0])
              if q == None:
                print("  Opps")
                sys.exit()
              #

            else:
              if verbose: print("  solo")

            #

            # Quilt fits
            #print("  Quilt(%s) %7s fits on row %2s side %s bay %d level %s" % \
            #(quilt[Q_CLASS], quilt[Q_ID], rack[R_ROW], rack[R_SIDE], rack[R_RBAY], rack[R_LEVEL])

            # Assign this quilt to this rack
            rack[R_REMAIN] = rack[R_REMAIN] - quilt[Q_WIDTH] - 0.5*2
            rack[R_QUILTS].append(quilt[Q_ID])

            # Assign rack to quilt
            quilt[Q_SLAT]  = rack[R_ID]

            found = True
            break

          else:
            if verbose: print("  Not high enough")
            failReason += "Not high enough "
            pass
          #
        else:
          if verbose: print("  Not wide enough")
          failReason += "Not wide enough "
          pass
        #
      else:
        if verbose: print("  Not right class", rack[R_ROW], over[O_ROW],\
           rack[R_SIDE],  over[O_SIDE],\
           rack[R_RBAY],  over[O_BAY],\
           rack[R_LEVEL], over[O_LEVEL])
        failReason += "Not right class "
        pass
      #  
    # end racks

    if (not found):
      print("Force, Not assigned: ", quilt[Q_ID], failReason)
    #

  #



  #####################################################################
  # Assign quilts to racks
  #####################################################################
  def Assign(self, quilt, verbose):

    found = False

    if verbose: print("Processing: %s, " % quilt[Q_ID])


    if self.IsQuiltForced(quilt[Q_ID]):
      print("Forced: ", quilt[Q_ID])
      return

    # For each rack
    for rack in self.racks:

      if (rack[R_CLASS] == 'X'): continue

      # Sanity checks
      if (rack[R_SWIDTH]*12 - 4.0 < rack[R_RWIDTH]):   # Slats need 2 inches on each side to engage the poles
        print("Width failure:", rack)
        sys.exit()

      if verbose: print("  Rack %d" % rack[R_ID])

      # If right class
      if quilt[Q_CLASS] == rack[R_CLASS]: 

        # Does quilt fit on the remaining width of this rack?
        if (quilt[Q_WIDTH]+0.5*2 <= rack[R_REMAIN]):

          # Does quilt fit in height?
          if (quilt[Q_HEIGHT] <= rack[R_HEIGHT]):

            # If there are other quilts on this slat
            if (len(rack[R_QUILTS]) > 0):

              # Find the size of the first quilt on this slat
              q = self.GetQuiltById(rack[R_QUILTS][0])
              if q == None:
                print("  Opps")
                sys.exit()
              #

              h = q[Q_HEIGHT]
              if h == 0: h = 1

              # Is the height of this quilt comperable to the others?
              percent = rack[R_TOLERANCE]
              if (math.fabs(quilt[Q_HEIGHT] - h)/h > percent):
                if verbose: print("  Not similar %d %d" % (quilt[Q_HEIGHT], h))
                continue
              #

            else:
              if verbose: print("  solo")

            #

            # Quilt fits
            if (0):
              print("  Quilt(%s) %7s fits on row %2s side %s bay %d level %s" % \
              (quilt[Q_CLASS], quilt[Q_ID], rack[R_ROW], rack[R_SIDE],
                  rack[R_RBAY], rack[R_LEVEL]))
            #

            # Assign this quilt to this rack
            rack[R_REMAIN] = rack[R_REMAIN] - quilt[Q_WIDTH] - 0.5*2
            rack[R_QUILTS].append(quilt[Q_ID])

            # Assign rack to quilt
            quilt[Q_SLAT]  = rack[R_ID]

            found = True
            break

          else:
            if verbose: print("  Not high enough")
            pass
          #
        else:
          if verbose: print("  Not wide enough")
          pass
        #
      else:
        if verbose: print("  Not right class" )
        pass
      #  
    # end racks

    if (not found):
        print("Not assigned: %s (W:%d H:%d C:%s)" %(quilt[Q_ID],
            quilt[Q_WIDTH], quilt[Q_HEIGHT], quilt[Q_CLASS]))
    #

  #


  #####################################################################
  # Generate the DXF files for each row
  #####################################################################
  def GenerateDxf(self):

    print("Generating DXF files")

    # Define some constants
    gap     = 1      # gap between quilt
    advance = 12*12  # Amount to advance down the page for each row
    pw      = 2      # Poles are two inches wide
    maxTs   = 5.0

    # Set a last value that will be different on first pass
    last = self.racks[len(self.racks)-1]

    # Open the master layout of all rows
    master = dxf.drawing("./DXF/Master.dxf")

    # Where to start on the page
    xOrg = 0
    yOrg = advance   # Start up a bit as we drop down first before printing

    name = None

    # For each rack
    for rack in self.racks:

      # Skip if Class is X (exclude)
      if (rack[R_CLASS] == 'X'): continue

      # If we changed rows/sides
      if (rack[R_ROW] != last[R_ROW]) or (rack[R_SIDE] != last[R_SIDE]):

        # Close last file
        if (name != None):

          # Add row Width
          s = "L=%d'%d\"" % (lastWidth/12, lastWidth%12)
          sheet.add(dxf.text(s, (90, yOrg-10), height = 4.0))
          master.add(dxf.text(s, (90, yOrg-10), height = 4.0))

          # Save the sheet
          sheet.save()

          del sheet
        #
           
        # Open new file
        name = "./DXF/Row_%d_%s.dxf" % (rack[R_ROW] , rack[R_SIDE])
        sheet = dxf.drawing(name)


        # Reset sheet variables
        xOrg = 0
        yOrg = yOrg - advance   # Advance down the page

        # Add row name
        s = "ROW: " + str(rack[R_ROW]) + '-' + rack[R_SIDE]
        sheet.add (dxf.text(s, (2, yOrg-10), height = 7.0))
        master.add(dxf.text(s, (2, yOrg-10), height = 7.0))


      # Same row/side
      else:

        # If we changed bays
        if (rack[self.R_BAY] != last[self.R_BAY]):

          # Point to next bay's origin
          xOrg = xOrg + last[R_RWIDTH] + pw
        #

      #


      # Get pole heights and widths
      lp = rack[R_LEFT]  * 12
      rp = rack[R_RIGHT] * 12

      # Get slat height
      if rack[R_LEVEL] == 'Top':
        sh = min(lp,rp)
      elif rack[R_LEVEL] == 'Mid':
        sh = min(lp,rp) - rack[R_HEIGHT]
      else:
        print("Invalid level")
        sys.exit()
      #

      # Draw left pole
      sheet.add(dxf.rectangle((xOrg, yOrg) , -pw, lp))
      master.add(dxf.rectangle((xOrg, yOrg) , -pw, lp))

      # Annotate height
      s = "%d'" % (rack[R_LEFT])
      sheet.add(dxf.text(s, (xOrg-pw, yOrg+lp+2), height = 4.0))
      master.add(dxf.text(s, (xOrg-pw, yOrg+lp+2), height = 4.0))

      # Draw right pole
      sheet.add(dxf.rectangle((xOrg+rack[R_RWIDTH], yOrg) , pw, rp))
      master.add(dxf.rectangle((xOrg+rack[R_RWIDTH], yOrg) , pw, rp))

      # Annotate height
      lastWidth = xOrg+rack[R_RWIDTH]+pw+pw
      s = "%d'" % (rack[R_RIGHT])
      sheet.add(dxf.text(s, (xOrg+rack[R_RWIDTH], yOrg+rp+2), height = 4.0))
      master.add(dxf.text(s, (xOrg+rack[R_RWIDTH], yOrg+rp+2), height = 4.0))

      # Add a gap between quilt
      x = xOrg + gap

      # If bay/level is empty
      if (len(rack[R_QUILTS]) != 0):

        # Annotate slat length
        s = str(rack[R_SWIDTH]) + "'"
        sheet.add (dxf.text(s, (xOrg+rack[R_RWIDTH]/2, yOrg+sh+2), height = 4.0))
        master.add(dxf.text(s, (xOrg+rack[R_RWIDTH]/2, yOrg+sh+2), height = 4.0))

        # For each quilt
        for qid in rack[R_QUILTS]:

          q = self.GetQuiltById(qid)

          # Draw quilts
          sheet.add(dxf.rectangle((x, yOrg+sh) , q[Q_WIDTH], -q[Q_HEIGHT]))
          master.add(dxf.rectangle((x, yOrg+sh) , q[Q_WIDTH], -q[Q_HEIGHT]))

          if (q[Q_WIDTH] > len(q[Q_ID])*maxTs):
            ang = 0.0
            xt = x+2
            yt = yOrg+sh-7
            ts = maxTs

          else:

            ang = 0.0
            xt = x+2
            yt = yOrg+sh-7
            ts = q[Q_WIDTH]/(len(q[Q_ID])+1)
            if (q[Q_HEIGHT] < ts):
              ts = q[Q_HEIGHT]
            if (ts > maxTs): ts = maxTs
          #

          # Draw quilt text
          t = q[Q_ID]
          sheet.add (dxf.text(t, (xt, yt), height = ts, rotation=ang))
          master.add(dxf.text(t, (xt, yt), height = ts, rotation=ang))

          # Print details on the quilt
          if (not self.nodetail):

            t = str(q[Q_WIDTH])
            sheet.add (dxf.text(t, (xt, yt-ts-1), height = ts, rotation=ang))
            master.add(dxf.text(t, (xt, yt-ts-1), height = ts, rotation=ang))

            t = str(q[Q_HEIGHT])
            sheet.add (dxf.text(t, (xt, yt-ts-1-ts-1), height = ts, rotation=ang))
            master.add (dxf.text(t, (xt, yt-ts-1-ts-1), height = ts, rotation=ang))

            if self.IsQuiltForced(q[Q_ID]):
                f = "*"
            else:
                f = ""
            #
            t = "%d%s%d%s%s" % (rack[R_ROW],rack[R_SIDE][0],rack[R_RBAY],rack[R_LEVEL][0],f)
            sheet.add (dxf.text(t, (xt, yt-ts-1-ts-1-ts-1), height = ts, rotation=ang))
            master.add(dxf.text(t, (xt, yt-ts-1-ts-1-ts-1), height = ts, rotation=ang))
          #

          # Move over width of quilt plus gap
          x = x + q[Q_WIDTH] + gap

        #

      #


      # Save last values
      last = rack

    #

    # Add row Width
    s = "L=%d'%d\"" % (lastWidth/12, lastWidth%12)
    sheet.add(dxf.text(s, (90, yOrg-10), height = 4.0))
    master.add(dxf.text(s, (90, yOrg-10), height = 4.0))

    # Save the sheet
    sheet.save()
    master.save()

  #

  #####################################################################
  # Generate PlanView DXF file
  # This generates a DXF that can be cut and pasted into the Lion's hall
  # floor plan drawing.
  #####################################################################
  def GeneratePlanView(self):

    SF = 1.0/12.0   # Scale factor

    print("Generating PlanView DXF file")

    # Define some constants
    advance = 150*SF    # Amount to advance down the page for each row
    pw      = 2*SF      # Poles are two inches wide
    hpw     = (pw/2)    # Poles are two inches wide
    bd      = 22.0*SF
    br      = bd/2.0

    # Set a last value that will be different on first pass
    last = self.racks[len(self.racks)-1]

    # Open the PlanView file
    planView = dxf.drawing("./DXF/PlanView.dxf")
    planView.add_style("ARIAL_BOLD")

    # Where to start on the page
    xOrg = 0
    yOrg = advance   # Start up a bit as we drop down first before printing

    name = None

    # For each rack
    for rack in self.racks:

      # Skip if Class is X (exclude)
      if (rack[R_CLASS] == 'X'): continue

      # If we changed rows
      if (rack[R_ROW] != last[R_ROW]):
           
        # Reset sheet variables
        xOrg = 0
        yOrg = yOrg - advance   # Advance down the page

        # Add row name
        s = "%d" % rack[R_ROW]
        planView.add(dxf.text(s, (36*SF, yOrg-0*SF), height = 2.0))

      # Same row
      else:

        # If we changed bays
        if (rack[self.R_BAY] != last[self.R_BAY]):

          # Point to next bay's origin
          xOrg = xOrg - (last[R_RWIDTH]*SF + pw)
        #

      #

      if (rack[R_SIDE] != last[R_SIDE]):

        # Reset sheet variables
        xOrg = 0
      #

      # Draw the two poles and the line between them
      planView.add(dxf.rectangle((xOrg-br, yOrg-br), bd, bd))
      planView.add(dxf.rectangle((xOrg-rack[R_RWIDTH]*SF-br, yOrg-br), bd,bd))
      planView.add(dxf.line((xOrg,yOrg), (xOrg-rack[R_RWIDTH]*SF,yOrg)))

      # Annotage the poles heights
      s = "%d'" % (rack[R_LEFT])
      planView.add(dxf.text(s, (xOrg+hpw, yOrg+13*SF), height = 1.5))
      s = "%d'" % (rack[R_RIGHT])
      planView.add(dxf.text(s, (xOrg-rack[R_RWIDTH]*SF-hpw, yOrg+13*SF), height = 1.5))

      # Annotate the slat and actual widths
      s = "%d'" % (rack[R_SWIDTH])
      if (rack[R_SIDE] == "Front"):
          if (rack[R_LEVEL] == "Top"):
            yOff = 0.5
          else:
            yOff = 2.0
      else:
          if (rack[R_LEVEL] == "Top"):
            yOff = -1.5
          else:
            yOff = -3.0
          #
      #
      planView.add(dxf.text(s, (xOrg-rack[R_RWIDTH]*SF/2, yOrg+yOff), height = 1.0))

      # Save last values
      last = rack

    #

    # Save the sheet
    planView.save()


  #

  #####################################################################
  # Get a single quilts information by its ID
  #####################################################################
  def GetQuiltById(self, qid):
    for q in self.quilts:
      if (q[Q_ID] == qid):
        return q
      #
    #
    return None
  #

  #####################################################################
  # Return True if the quilt is forced
  #####################################################################
  def IsQuiltForced(self, qid):
    for over in self.overrides:
      if (over[O_QID] == qid):
        return True
    #
    return False
  #


# end of class


#####################################################################
# Main
#####################################################################
if __name__ == "__main__":


  # Create a quilt object
  q = Q()

  # Start processing
  q.Process()
