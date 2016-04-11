# Author: Michael T. Fang <mfang@caltech.edu>

""" Python GDS Library
Library for creating geometries commonly found in superconducting circuits

Change Log:
2/22/2016 - Fixed bug in meander function where meanders would be written with
incorrect lengths

"""

# Written using gdspy 0.7.1 and numpy 1.10.1
from numpy import *
import gdspy

print('Using gdspy module version ' + gdspy.__version__)

class CPWPath:
    """ Create a new CPW object
    width - center conductor width
    gap - distance between center condctor and ground plane
    layer - specify layer of CPW object
    datatype -  GDS datatype (0-255)
    """
    def __init__(self, width, gap, layer = 0, datatype = 0, cellName = None):
        self.width = width
        self.gap = gap
        self.initalDirection = '+x'
        self.initalOrientation = False
        self.path = None
        self.spec = {'layer': layer, 'datatype': datatype}
        self.cellName = cellName

    def start(self, start = [0, 0], direction = None):
        ### Start a CPW path specified by start coordinates and a direction
        ### direction: {+x, -x, +y, -y} or angle (in radians)
        if direction is not None:
            # Get direction from CPW class
            self.initalDirection = direction
        # Define the distance
        d = self.width + self.gap
        self.path = gdspy.Path(self.gap,(start[0],start[1]),number_of_paths = 2,
                                                            distance=d)

    def end(self):
        cellName = self.cellName
        cellName.add(self.path)
        # addPolyToCell(gdspy.PolygonSet(self.path.polygons), cellName)

    def straight(self, distance, widthEnd = None, gapEnd = None):
        ### Draw a straight CPW segment in the direction following the last path
        ### Tapers can be created by specifying a termination width and gap
        spec = self.spec
        if self.initalOrientation is False:
            direction = self.initalDirection
            self.initalOrientation = True
        else:
            direction = self.path.direction
        if widthEnd is None:
            # Get width from CPW class
            widthEnd = self.width
        else:
            # Update the width
            self.width = widthEnd
        if gapEnd is None:
            # Get gap from CPW class
            gapEnd = self.gap
        else:
            # Update the gap
            self.gap = gapEnd
        # Change the final distance
        distanceEnd = widthEnd + gapEnd
        # Add segment
        self.path.segment(distance, direction, final_distance = distanceEnd, final_width = gapEnd, **spec)

    def openGap(self, distance, widthEnd = None, gapEnd = None):
        ### Draw a straight CPW gap segment in the direction following the last path
        ### Tapers can be created by specifying a termination width and gap
        if self.initalOrientation is False:
            direction = self.initalDirection
            self.initalOrientation = True
        else:
            direction = self.path.direction
        spec = self.spec
        # Get width from CPW class
        widthStart = self.width
        # Get gap from CPW class
        gapStart= self.gap
        totalWidthStart = widthStart + 2*gapStart
        if widthEnd is None:
            # Get width from CPW class
            widthEnd = widthStart
        else:
            # Update the width
            self.width = widthEnd
        if gapEnd is None:
            # Get gap from CPW class
            gapEnd = gapStart
        else:
            # Update the gap
            self.gap = gapEnd
        totalWidthEnd = widthEnd + 2*gapEnd
        # Change the final distance
        distanceEnd = widthEnd + gapEnd
        # Add segment
        self.path.segment(1E-9, direction, final_distance = totalWidthEnd/2,
                                            final_width = totalWidthStart/2, **spec)
        self.path.segment(distance, direction, final_distance = totalWidthEnd/2,
                                            final_width = totalWidthEnd/2, **spec)
        self.path.segment(-1E-9, direction, final_distance = distanceEnd,
                                            final_width = gapEnd, **spec)

    def openGapFillet(self, distance, gapType, filletRadius = 10, direction = None):
        ### Draw a straight CPW gap segment in the direction following the last path with a fillet
        ### Gap type is either 'beg' or 'end' to specify where fillet goes
        gap = self.gap
        width = self.width
        spec = self.spec
        if gapType == 'beg':
            if direction is None:
                direction = self.initalDirection
        if gapType == 'end':
            if direction is None:
                direction = self.path.direction
        cellName = self.cellName
        x = self.path.x
        y = self.path.y
        if direction == '+x':
            theta = 0
        elif direction == '+y':
            theta = pi/2
        elif direction == '-y':
            theta = 3*pi/2
        elif direction == '-x':
            theta = pi
        else:
            theta = direction

        points = self.rectPathPivot(x, y, 0, distance, width + 2*gap, theta)
        gapPoly = gdspy.Polygon(points, **spec)
        gapPoly.fillet(filletRadius)

        if gapType == 'beg':
            points = self.rectPathPivot(x, y, distance - filletRadius, distance, width + 2*gap, theta)
        elif gapType == 'end':
            points = self.rectPathPivot(x, y, 0, filletRadius, width + 2*gap, theta)
        gapPolyNoFillet = gdspy.Polygon(points, **spec)

        union = gdspy.boolean([gapPolyNoFillet, gapPoly],
            lambda gpnf, gp: gpnf or gp, **spec)

        # Correct for path offset
        if direction == '+x':
            self.path.x = x + distance
            self.path.y = y
        elif direction == '+y':
            self.path.x = x
            self.path.y = y + distance
        elif direction == '-y':
            self.path.x = x
            self.path.y = y - distance
        elif direction == '-x':
            self.path.x = x - distance
            self.path.y = y
        else:
            self.path.x  = x + sin(theta)*distance
            self.path.y  = y + cos(theta)*distance

        # Inner fillet position definitions
        if gapType == 'beg':
            x = self.path.x
            y = self.path.y
        elif gapType == 'end':
            x = x - cos(theta)*(2*filletRadius)
            y = y - sin(theta)*(2*filletRadius)

        # Create masks for fillet and so subtraction
        points = self.rectPathPivot(x, y, 0, 2*filletRadius, width, theta)
        rectMask = gdspy.Polygon(points, **spec)
        rectMask.fillet(filletRadius)
        if gapType == 'beg':
            points = self.rectPathPivot(x, y, 0, filletRadius, width, theta)
        elif gapType == 'end':
            points = self.rectPathPivot(x, y, filletRadius, 2*filletRadius, width, theta)
        rect = gdspy.Polygon(points, **spec)
        subtraction = gdspy.boolean([rectMask, rect],
            lambda rem, re: re and not rem, **spec)

        # Add polygons to cell
        cellName.add(subtraction)
        cellName.add(union)


    def rectPathPivot(self, x, y,start, stop, width, theta):
        # Create points for a polygon pivoted around the current path position (x,y)
        # at an angle theta that is (stop - start) long and width wide.
        begLeftx  = x - sin(theta)*width/2 + cos(theta)*start
        begLefty  = y + cos(theta)*width/2 + sin(theta)*start
        begRightx = x + sin(theta)*width/2 + cos(theta)*start
        begRighty = y - cos(theta)*width/2 + sin(theta)*start
        endLeftx  = x - sin(theta)*width/2 + cos(theta)*stop
        endLefty  = y + cos(theta)*width/2 + sin(theta)*stop
        endRightx = x + sin(theta)*width/2 + cos(theta)*stop
        endRighty = y - cos(theta)*width/2 + sin(theta)*stop
        points = [(begLeftx, begLefty), (begRightx, begRighty), (endRightx, endRighty), (endLeftx, endLefty)]
        return points

    def bend(self, radius, angle, widthEnd = None, gapEnd = None, bendPoints = 100):
        ### Add a CPW bend with specified angle and radius
        ### Use 'l' ('r') for right angle ccw (cw) turn
        ### Use 'll'('rr') for 180 degree ccw (cw) turn
        ### Specify widthEnd and gapEnd for a curved taper
        ### Increase bend points for a smoother bend
        spec = self.spec
        if widthEnd is None:
            # Get width from CPW class
            widthEnd = self.width
        else:
            # Update the width
            self.width = widthEnd
        if gapEnd is None:
            # Get gap from CPW class
            gapEnd = self.gap
        else:
            # Update the gap
            self.gap = gapEnd
        # Change the final distance
        distanceEnd = widthEnd + gapEnd
        # Add turn to path
        self.path.turn(radius, angle, final_width = gapEnd,
            number_of_points = bendPoints, final_distance = distanceEnd, **spec)

    def meander(self, lengthTotal, radius, straightLength, initialAngle = 'll'
                                                            , bendPoints = 100):
        spec = self.spec
        prevLen = self.len()
        while lengthTotal - (radius*pi + straightLength) > (self.len() - prevLen):
            self.straight(straightLength)
            self.bend(radius, initialAngle, bendPoints = bendPoints)
            if initialAngle is 'll':
                initialAngle = 'rr'
            elif initialAngle is 'rr':
                initialAngle = 'll'
            elif initialAngle is 'l':
                initialAngle = 'rr'
            elif initialAngle is 'r':
                initialAngle = 'll'
            elif initialAngle % (2*pi) < pi:
                initialAngle = 'rr'
            elif initialAngle % (2*pi) > pi:
                initialAngle = 'll'
            else:
                initialAngle = 'll'
        # The tail end of the meander
        if (lengthTotal -  (self.len() - prevLen)) < straightLength:
            # Not long enough to finish straight segment
            self.straight(lengthTotal - (self.len() - prevLen))
        else: # Can finish straight segment, need to end on a curve
            self.straight(straightLength)
            lastAngle = abs((lengthTotal - (self.len() - prevLen))/(radius)) # Angle needed for ending
            if initialAngle is 'll':
                lastAngle = lastAngle
                self.bend(radius, lastAngle, bendPoints = bendPoints)
            elif initialAngle is 'rr':
                lastAngle = -lastAngle
                self.bend(radius, lastAngle, bendPoints = bendPoints)

    def len(self):
        # Pass through length attribute from path object
        return self.path.length

    def pos(self):
        # Pass through position attribute from path object
        return [self.path.x, self.path.y]

    def dir(self):
        # Pass through direction attribute from path object
        return self.path.direction

    def useAsMask(self, groundPlane = None):
        ### Generates metal from groundPlane using CPW as a negative mask
        ### Make a fake 1000x1000 at origin ground plane if none given
        ### Returns resulting object
        spec = self.spec
        if groundPlane is None:
            groundPlane = gdspy.Rectangle((-500, -500), (500, 500), 0)
        # Create a PolygonSet from CPW path
        cpwPolySet = self.makePolySet(self.path)
        # Apply boolean operation
        return gdspy.boolean([groundPlane, cpwPolySet],
            lambda groundPlane, cpwPolySet: groundPlane and not cpwPolySet, **spec)

    def makePolySet(self, path):
        ### Converts a path object to a polyset object
        return gdspy.PolygonSet(self.path.polygons)


def addPolyToCell(addThis, cell):
        ### cell - specify which GDS cell to add to
        cell.add(addThis)

def mask(subtractThis, addThis = None, layer = 1, datatype = 1):
    ### Makes a mask from two objects of the type:
    ### Polygon, PolygonSet, CellReference, CellArray,
    ### or an array-like[N][2] of vertices of a polygon.
    ### cell - specify which GDS cell to add mask to
    ### Make a fake 1000x1000 at origin ground plane if addThis not given
    spec = {'layer': layer, 'datatype': datatype}
    if addThis is None:
        addThis = gdspy.Rectangle((-500, -500), (500, 500), 0)
    # Apply boolean operation and add boolean to cell
    return gdspy.boolean([addThis, subtractThis],
        lambda addThis, subtractThis: addThis and not subtractThis, **spec)

def union(one, two, layer = 1, datatype = 1):
    ### Makes a mask from two objects of the type:
    ### Polygon, PolygonSet, CellReference, CellArray,
    ### or an array-like[N][2] of vertices of a polygon.
    spec = {'layer': layer, 'datatype': datatype}
    # Apply boolean operation and add boolean to cell
    return gdspy.boolean([one, two],
        lambda one, two: one or two, **spec)
