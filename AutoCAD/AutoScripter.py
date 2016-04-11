# Author: Michael T. Fang <mfang@caltech.edu>

""" Easy AutoCAD Scripter
This module simplies the drawing process for scripts that automate AutoCAD.
It draws various shapes by printing to a script file defined by the user,
which is then run on AutoCAD.

*** NOTE: When exporting dxf file in AutoCAD, use the 2000 DXF version format.

Notes for AutoLISP:

Erasing everything from a specified layer:
(if (setq ss (ssget "_X" '((8 . "LAYER")))) (command "_.erase" ss ""))


"""
from math import *
import subprocess
from os import getcwd
import shlex

class newScript:
    def __init__(self,filename):
        self.filename = filename
        self.script = open(filename,'w')
        self.script.write("(setvar \"CmdEcho\" 0)\n-osnap\n\n") # Script set up commands
        self.prevAngleRad = 0.0
        self.prevEnd = [0.0,0.0]

    def runScript(self,pathAutoCAD):
        """ Runs AutoCAD with the script you are working with via subprocess"""
        # Get acad.exe path from AutoCAD Folder
        programPath = '\"%s%s\"' % (pathAutoCAD, "\\acad.exe")
        # Get script path from current Folder
        scriptPath = '\"%s%s%s\"' % (getcwd(), "\\",self.filename)
        # Commend to have AutoCAD run script file
        command = "%s%s%s" % (programPath, ' /b ', scriptPath)
        # Parse command
        args = shlex.split(command)
        #E xecute command
        p = subprocess.Popen(args)

    def exportDXF(self):
        """ Exports a DXF file (version 2000) with the same name as script """
        nameDXF = self.filename.replace(".scr", "")
        # Zoom out to full view, not sure where else to have this happen
        self.script.write("ZOOM\nALL\n")
        self.script.write("DXFOUT\n%s\nV\nLT2000\n\n" % nameDXF)

    def addLayer(self, name = "NameMe", color = [255,255,255]):
        """ Creates a new layer with the specified name and
            RGB color"""
        self.script.write("-LAYER\nMAKE\n%s\n" % name)
        self.script.write("COLOR\nTRUECOLOR\n%d,%d,%d\n\n\n" \
            % tuple(color))

    def setLayer(self, name):
        """ Changes current layer to specified by name"""
        self.script.write("-LAYER\nSET\n%s\n\n" % name)

    def selectAllOnLayer(self, layerName):
        """ Selects all objects on layer """
        self.script.write("(ssget \"_X\" \'((8 . \"%s\")))\n" % layerName)
    def convertPolyToRegion(self, layerName):
        """ Converts all polyline objects on a layer to a region object"""
        self.script.write("(if (setq ss (ssget \"_X\" \'((8 . \"%s\")))) (command \"_.region\" ss \"\"))\n" % layerName)

    def convertRegionToPoly(self, layerName):
        """ Converts all region objects on a layer to polyline objects """
        self.script.write("EXPLODE\n")
        self.script.write("(ssget \"_X\" \'((8 . \"%s\")))\n\n\n" % layerName)
        self.script.write("EXPLODE\n")
        self.script.write("(ssget \"_X\" \'((8 . \"%s\")))\n\n\n" % layerName)
        self.script.write("EXPLODE\n")
        self.script.write("(ssget \"_X\" \'((8 . \"%s\")))\n\n\n" % layerName)
        self.script.write("PEDIT\nM\n")
        self.script.write("(ssget \"_X\" \'((8 . \"%s\")))\n\nY\nJ\nJ\nE\n\n\n" % layerName)
        #self.script.write("(ssget \"_X\" \'((8 . \"%s\")))\n\n" % layerName)

    def subtractLayers(self, layerTrash, layerKeep):
        """ Subtracts layerTrash from layerKeep """
        self.script.write("SUBTRACT\n")
        self.script.write("(ssget \"_X\" \'((8 . \"%s\")))\n\n" % layerKeep)
        self.script.write("(ssget \"_X\" \'((8 . \"%s\")))\n\n" % layerTrash)

    def addRect(self, base, xlen, ylen):
        """ Adds a rectangle with corners (base[0],base[1]) and
            (base[0] + xlen, base[1] + ylen)"""
        self.script.write("RECTANGLE\n%f,%f\n%f,%f\n" \
            % (base[0], base[1], base[0] + xlen, base[1] + ylen))
    def addCPWRectGap(self, width, gap, length, start, startAngleRad):
        """ Adds a rectangle with corners (base[0],base[1]) and
            (base[0] + xlen, base[1] + ylen)"""
        self.script.write("PLINE\n")
        self.rotateAndWritePoint(startAngleRad, start[0], \
            start[1],start)
        self.rotateAndWritePoint(startAngleRad, start[0], \
            start[1] - width/2 - gap,start)
        self.rotateAndWritePoint(startAngleRad, start[0] + length, \
            start[1] - width/2 - gap,start)
        self.rotateAndWritePoint(startAngleRad, start[0] + length, \
            start[1] + width/2 + gap,start)
        self.rotateAndWritePoint(startAngleRad, start[0], \
            start[1] + width/2 + gap,start)
        self.script.write("c\n")
        self.prevAngleRad = startAngleRad
        self.prevEnd = [start[0] + length*cos(startAngleRad), start[1] + length*sin(startAngleRad)]

    def addCircle(self, base, r):
        """ Adds a circle with radius r with center (base[0],base[1])"""
        self.script.write("CIRCLE\n%f,%f\n%f\n" % (base[0],base[1],r))

    def addCircleArray(self, base, r, space = [2,2], nRepeat = [2,2]):
        """ Repeats a circle nRepeat times upwards and rightwards with
            separation given by space"""
        self.script.write("CIRCLE\n%f,%f\n%f\n" % (base[0],base[1], r))
        self.script.write("ARRAY\nLAST\n\n\n") # Array the most recent object
        self.script.write("%d\n%d\n" % tuple(nRepeat)) # Column and row repeat
        if nRepeat[0] == 1:
            self.script.write("%f\n" % space[1]) # Spacing for columns
        elif nRepeat[1] == 1:
            self.script.write("%f\n" % space[0]) # Spacing for rows
        else:
            self.script.write("%f\n%f\n" % tuple(space))
    def addCPWStraightSrtEnd(self, width, gap, start, end):
        """ Adds a coplanar waveguide with the specified width and gap from start to end"""
        [disp, theta] = self.getDisplacementAndAngle(start, end)
        self.script.write("PLINE\n")
        self.rotateAndWritePoint(theta, start[0], \
            start[1] - width/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] - width/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] - width/2 - gap,start)
        self.rotateAndWritePoint(theta, start[0], \
            start[1] - width/2 - gap,start)
        self.script.write("c\n")
        self.script.write("PLINE\n")
        self.rotateAndWritePoint(theta, start[0], \
            start[1] + width/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] + width/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] + width/2 + gap,start)
        self.rotateAndWritePoint(theta, start[0], \
            start[1] + width/2 + gap,start)
        self.script.write("c\n")
        self.prevAngleRad = theta
        self.prevEnd = end

    def addCPWStraightLenAng(self, width, gap, length, start, startAngleRad):
        """ For cases when defining end coordinate relative to start in polar
            coordinate is more convenient."""
        end = [start[0] + length*cos(startAngleRad), start[1] + length*sin(startAngleRad)]
        self.addCPWStraightSrtEnd(width, gap, start, end)

    def rotateAndWritePoint(self,theta,x,y,pivot):
        """ Rotates the specified point (x,y) by an angle theta
            around the pivot and write the result to the script"""
        [x_rot,y_rot] = self.rotatePoint(theta,x,y,pivot)
        self.script.write("%f,%f\n" \
            % (x_rot, y_rot))

    def rotatePoint(self,theta,x,y,pivot):
        """ Rotates the specified point (x,y) by an angle theta
            around the pivot"""
        x_rot = cos(theta)*(x - pivot[0]) \
            - sin(theta)*(y - pivot[1]) + pivot[0]
        y_rot = sin(theta)*(x - pivot[0])  \
            + cos(theta)*(y - pivot[1]) + pivot[1]
        return [x_rot,y_rot]

    def getDisplacementAndAngle(self, start, end):
        """ Does what it says"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        disp = (dx**2 + dy**2)**0.5
        if dx == 0 and dy > 0:
            theta = pi/2
        elif dx == 0 and dy < 0:
            theta = -pi/2
        elif dx < 0:
            theta = atan(dy/dx) + pi
        else:
            theta = atan(dy/dx)
        return [disp, theta]

    def addCPWRamp(self, widthStart, gapStart, widthEnd, gapEnd, start, end):
        """ Adds a coplanar waveguide with a linear ramp."""
        [disp, theta] = self.getDisplacementAndAngle(start, end)
        # Right side etch pattern
        self.script.write("PLINE\n")
        self.rotateAndWritePoint(theta, start[0], \
            start[1] - widthStart/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] - widthEnd/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] - widthEnd/2 - gapEnd,start)
        self.rotateAndWritePoint(theta, start[0], \
            start[1] - widthStart/2 - gapStart,start)
        self.script.write("c\n")
        # Left side etch pattern
        self.script.write("PLINE\n")
        self.rotateAndWritePoint(theta, start[0], \
            start[1] + widthStart/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] + widthEnd/2,start)
        self.rotateAndWritePoint(theta, start[0] + disp, \
            start[1] + widthEnd/2 + gapEnd,start)
        self.rotateAndWritePoint(theta, start[0], \
            start[1] + widthStart/2 + gapStart,start)
        self.script.write("c\n")
        self.prevAngleRad = theta # Keeping track of angles
        self.prevEnd = end # Keeping track of end points

    def addCPWRampLenAng(self, widthStart, gapStart, widthEnd, gapEnd, length, start, startAngleRad):
        """ For cases when defining end coordinate relative to start in polar
            coordinate is more convenient."""
        end = [start[0] + length*cos(startAngleRad), start[1] + length*sin(startAngleRad)]
        self.addCPWRamp(widthStart, gapStart, widthEnd, gapEnd, start, end)

    def addCPWAngBend(self, width, gap, radius, angle, start, startAngleRad = 0):
        """ Adds a coplanar waveguide with a bend from startAngle to angle.
            Angle should be between -180 and 180 degrees. The radius of
            the bend is defined from the middle of center the trace.
            AutoCAD can only draw arcs clockwise, so the code has to be a bit
            verbose and tedious. """
        angleRad = pi*angle/180
        rw2 = radius + width/2
        rw2g = radius + width/2 + gap

        if angle > 0:
            # Center arc axis is above the inital point for clockwise bend
            center = [start[0], start[1] + radius]
            self.CPWAngBendHelperPositive(center, start, radius, width ,gap, angleRad, startAngleRad)
            x = start[0] + radius*sin(angleRad)
            y = start[1] + radius - radius*cos(angleRad)
        elif angle < 0:
            # Center arc axis is below the inital point for counterclockwise arc
            center = [start[0], start[1] - radius]
            self.CPWAngBendHelperNegative(center, start, radius, width ,gap, angleRad, startAngleRad)
            x = start[0] - radius*sin(angleRad)
            y = start[1] - radius + radius*cos(angleRad)

        self.prevAngleRad = startAngleRad + angleRad # Keeping track of angles
        self.prevEnd = self.rotatePoint(startAngleRad,x,y,start) # Keeping track of end points
        self.joinAll()

    def joinAll(self):
        """ Join all into a single polyline """
        self.script.write("PEDIT\nM\nALL\n\n\nJ\n\n\n")

    def CPWAngBendHelperPositive(self, center, start, radius, width ,gap, angleRad ,startAngleRad):
        """ This is pretty much just the ugly geometry part of the bent CPW with angleRad > 0"""
        for i in range(0,2):
            # i = 0 makes the right side etch pattern
            # i = 1 makes the left side etch pattern
            if i == 0:
                sign = 1
            else:
                sign = -1
            # Some short hard notation
            rw2 = radius + sign*width/2
            rw2g = radius + sign*width/2 + sign*gap
            # Inner arc
            self.script.write("ARC\nC\n")
            self.rotateAndWritePoint(startAngleRad, center[0], center[1],start)
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] - rw2, start)
            arcEnd = [center[0] + rw2*sin(angleRad), \
                center[1] - rw2*cos(angleRad)]
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1], start)
            # Connecting line
            self.script.write("LINE\n")
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1],start)
            self.rotateAndWritePoint(startAngleRad, arcEnd[0] + sign*gap*sin(angleRad), \
                arcEnd[1] - sign*gap*cos(angleRad),start)
            # Inner arc
            self.script.write("\nARC\nC\n")
            self.rotateAndWritePoint(startAngleRad, center[0], center[1],start)
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] - rw2g, start)
            arcEnd = [center[0] + rw2g*sin(angleRad), \
                center[1] - rw2g*cos(angleRad)]
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1], start)
            # Connecting line
            self.script.write("LINE\n")
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] - rw2, start)
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] - rw2g, start)
            self.script.write("\n")

    def CPWAngBendHelperNegative(self, center, start, radius, width ,gap, angleRad ,startAngleRad):
        """ This is pretty much just the ugly geometry part of the bent CPW with angleRad < 0"""
        angleRad = -angleRad
        for i in range(0,2):
            # i = 0 makes the right side etch pattern
            # i = 1 makes the left side etch pattern
            if i == 0:
                sign = 1
            else:
                sign = -1
            # Some short hard notation
            rw2 = radius + sign*width/2
            rw2g = radius + sign*width/2 + sign*gap

            # Inner arc
            self.script.write("ARC\nC\n")
            self.rotateAndWritePoint(startAngleRad, center[0], center[1], start)
            arcEnd = [center[0] + rw2*sin(angleRad), \
                center[1] + rw2*cos(angleRad)]
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1], start)
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] + rw2, start)
            # Connecting line
            self.script.write("LINE\n")
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] + rw2, start)
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] + rw2g, start)
            # Outer arc
            self.script.write("\nARC\nC\n")
            self.rotateAndWritePoint(startAngleRad, center[0], center[1],start)
            arcEnd = [center[0] + rw2g*sin(angleRad), \
                center[1] + rw2g*cos(angleRad)]
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1], start)
            self.rotateAndWritePoint(startAngleRad, center[0], center[1] + rw2g, start)
            # Connecting line
            self.script.write("LINE\n")
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1], start)
            self.rotateAndWritePoint(startAngleRad, arcEnd[0], arcEnd[1], start)
            self.rotateAndWritePoint(startAngleRad, arcEnd[0] - sign*gap*sin(angleRad), \
                arcEnd[1] - sign*gap*cos(angleRad),start)
            self.script.write("\n")

    def CPWMeander(self, width, gap, lengthTotal, radius, straightLength, startPhaseRad, start, startAngleRad):
        """ Generates a CPW meander which starts with a phase defined as follows: http://i.imgur.com/K03NLCl.png
            lengthTotal, radius, and straightLength more or less set the overall size of the meander"""
        startPhaseRad = startPhaseRad % (2*pi)
        lengthSoFar = 0 # Metric for length accumulation and stopping
        turn = 0 # Which way do I turn next? Clockwise (CW) or CCW?

        # First bend of meander
        if startPhaseRad == 0:
            self.addCPWAngBend(width, gap, radius, -180, self.prevEnd, self.prevAngleRad)
            lengthSoFar +=  radius*pi
            turn = 1
        elif startPhaseRad == pi:
            self.addCPWAngBend(width, gap, radius, 180, self.prevEnd, self.prevAngleRad)
            lengthSoFar += radius*pi
            turn = -1
        else:
            self.addCPWAngBend(width, gap, radius, 180*(startPhaseRad - pi)/pi, self.prevEnd, self.prevAngleRad)
            lengthSoFar += abs(radius*(startPhaseRad - pi))
            # Figure out which diretion to turn next
            if startPhaseRad < pi and startPhaseRad > 0:
                turn = 1
            else:
                turn = -1
        # The middle bulk of the meander
        while lengthTotal - (radius*pi + straightLength) > lengthSoFar:
            self.addCPWStraightLenAng(width, gap, straightLength, self.prevEnd, self.prevAngleRad)
            self.addCPWAngBend(width, gap, radius, turn*180, self.prevEnd, self.prevAngleRad)
            turn = -turn
            lengthSoFar += straightLength + radius*pi
        # The tail end of the meander
        if (lengthTotal - lengthSoFar) < straightLength: # Not long enough to finish straight segment
            self.addCPWStraightLenAng(width, gap, lengthTotal - lengthSoFar, self.prevEnd, self.prevAngleRad)
            lengthSoFar += lengthTotal - lengthSoFar
        else: # Can finish straight segment, need to end on a curve
            self.addCPWStraightLenAng(width, gap, straightLength, self.prevEnd, self.prevAngleRad)
            lastAngle = 180*(lengthTotal - lengthSoFar - straightLength)/(pi*radius) # Angle needed for ending
            self.addCPWAngBend(width, gap, radius, turn*lastAngle, self.prevEnd, self.prevAngleRad)
            lengthSoFar += straightLength + pi*lastAngle/180*radius

    def launchPadBegin(self, padWidth, totalWidth, traceWidth, traceGap, padLength, rampLength, start, startAngleRad):
        """  Begin a trace with a lunach pad """
        padGap = (totalWidth - padWidth)/2
        self.addCPWRectGap(padWidth, padGap, padGap, start, startAngleRad)
        self.addCPWStraightLenAng(padWidth, padGap, padLength, self.prevEnd, self.prevAngleRad)
        self.addCPWRampLenAng(padWidth, padGap, traceWidth, traceGap, rampLength, self.prevEnd, self.prevAngleRad)

    def launchPadEnd(self, padWidth, totalWidth, traceWidth, traceGap, padLength, rampLength, start, startAngleRad):
        """ End a trace with a lunach pad """
        padGap = (totalWidth - padWidth)/2
        self.addCPWRampLenAng(traceWidth, traceGap, padWidth, padGap, rampLength, self.prevEnd, self.prevAngleRad)
        self.addCPWStraightLenAng(padWidth, padGap, padLength, self.prevEnd, self.prevAngleRad)
        self.addCPWRectGap(padWidth, padGap, padGap, self.prevEnd, self.prevAngleRad)

# Make a complex CPW trace (See here: http://i.imgur.com/mGCyDBt.png)
# a = AutoScripter('test.scr')
# width = 4
# gap = 4
# width2 = 10
# gap2 = 10
# sign = 1
# a.addLayer("Frame", [250,50,50])
# a.addRect(base = [0,0], xlen = 10000, ylen = 10000)
# a.addLayer("CPW", [50,250,50])
# a.launchPadBegin(150, 300, width, gap, 200, 200, [3000,200], startAngleRad = pi/2)
# a.addCPWAngBend(width, gap, 100, -45, a.prevEnd, a.prevAngleRad)
# a.addCPWStraightLenAng(width, gap, length = 200, start = a.prevEnd, startAngleRad = a.prevAngleRad)
# a.addCPWAngBend(width, gap, 100, 45, a.prevEnd, a.prevAngleRad)
# for i in range(2,10):
#     sign = -sign
#     a.addCPWStraightLenAng(width, gap, 100, a.prevEnd, a.prevAngleRad)
#     a.addCPWAngBend(width, gap, 2*(width + gap)*i, -180*sign, a.prevEnd, a.prevAngleRad)
# for i in range(0,3):
#     a.addCPWStraightLenAng(width, gap, 100, a.prevEnd, a.prevAngleRad)
#     a.addCPWAngBend(width, gap, 2*(width + gap), -90, a.prevEnd, a.prevAngleRad)
# for i in range(0,3):
#     a.addCPWAngBend(width, gap, 4*(width + gap), 90, a.prevEnd, a.prevAngleRad)
# a.addCPWStraightLenAng(width, gap, 500, a.prevEnd, a.prevAngleRad)
# a.CPWMeander(width, gap, 2500, 25, 150, -pi/3, a.prevEnd, a.prevAngleRad)
# a.addCPWRampLenAng(width, gap, width2, gap2, 50, a.prevEnd, a.prevAngleRad)
# a.CPWMeander(width2, gap2, 2500, 25, 150, pi/2, a.prevEnd, a.prevAngleRad)
# a.addCPWRampLenAng(width2, gap2, width/2, gap/2, 100, a.prevEnd, a.prevAngleRad)
# a.addCPWStraightLenAng(width/2, gap/2, 200, a.prevEnd, a.prevAngleRad)
# a.addCPWAngBend(width/2, gap/2, 100, 30, a.prevEnd, a.prevAngleRad)
# a.launchPadEnd(150, 300, width/2, gap/2, 200, 200, a.prevEnd, a.prevAngleRad)
