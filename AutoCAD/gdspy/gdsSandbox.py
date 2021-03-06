from numpy import *
import gdspy
import gdslib
deviceName = '2016Jan18_Resonators'
device = gdspy.Cell(deviceName)

# FREQUENCY DESIGN
# [1] Coplanar Waveguide Circuits, Components, and Systems by Rainee Simons
c = 3E8;
er = 11.9 # Substrate dielectric constant
ereff = (1+er)/2; # [1] Eq. 2.30


# BOUNDARY DEFINITIONS
# Boundary of section of chip containing features
spec = {'layer': 1, 'datatype': 0}
featuresBndy = gdspy.Path(1, (0,0))
featuresBndy.segment(5000, '+y', **spec)
featuresBndy.segment(10000, '+x', **spec)
featuresBndy.segment(5000, '-y', **spec)
featuresBndy.segment(10000, '-x', **spec)
gdslib.addPolyToCell(featuresBndy, device)

# Boundary of the entire 1 cm chip
spec = {'layer': 2, 'datatype': 0}
chipBndy = gdspy.Path(1, (0,0))
chipBndy.segment(10000, '+y', **spec)
chipBndy.segment(10000, '+x', **spec)
chipBndy.segment(10000, '-y', **spec)
chipBndy.segment(10000, '-x', **spec)
gdslib.addPolyToCell(chipBndy, device)

# IDK what this is for honestly. It's on Paul's design
spec = {'layer': 3, 'datatype': 0}
chipBndy = gdspy.Path(1, (2500,10000))
chipBndy.segment(3000, '-y', **spec)
chipBndy.segment(5000, '+x', **spec)
chipBndy.segment(3000, '+y', **spec)
chipBndy.segment(5000, '-x', **spec)
gdslib.addPolyToCell(chipBndy, device)

# FEEDLINE
cpwfeed = gdslib.CPWPath(300,150,layer = 5)

cpwfeed.start([1125,100],'+y')
# cpwfeed.start([750,100],'+y')
cpwfeed.openGap(150)
cpwfeed.straight(250)
cpwfeed.straight(250, widthEnd = 10, gapEnd = 5)
cpwfeed.straight(250)
cpwfeed.bend(150, 'l')
cpwfeed.bend(150, 'r')
cpwfeed.straight(2500 - 1000 - 3*150)
cpwfeed.bend(150, 'r')
cpwfeed.straight(8200)
cpwfeed.bend(150, 'r')
cpwfeed.straight(2500 - 1000 - 3*150)
cpwfeed.bend(150, 'r')
cpwfeed.bend(150, 'l')
cpwfeed.straight(250)
cpwfeed.straight(250, widthEnd = 300, gapEnd = 150)
cpwfeed.straight(250)
cpwfeed.openGap(150)
gdslib.addPolyToCell(gdspy.PolygonSet(cpwfeed.path.polygons), device)

# BOTTOM RESONATOR ARRAY
f = linspace(6E9,6.1E9,6) # Fundamental frequency
l4 = c/sqrt(ereff)/4./f*1E6 # length for lambda/4 resonator
print(l4)

for i in range(0,5):
    totalLength = l4[i]
    openDis = 10
    capDist = 10*(1+i)
    cpwSrtExtend = 200
    bendRad = 100
    meanderLen = totalLength - openDis - capDist - cpwSrtExtend - pi*bendRad
    exec("cpw" + str(i) + " = gdslib.CPWPath(10,5,layer = 6)")
    exec("cpw" + str(i) + ".start([1900+ 625 + 1250*" + str(i) + ",2500 - 25],'+x')")
    exec("cpw" + str(i) + ".openGap(openDis)")
    exec("cpw" + str(i) + ".straight(capDist)")
    exec("cpw" + str(i) + ".bend(bendRad, 'r')")
    exec("cpw" + str(i) + ".straight(cpwSrtExtend)")
    exec("cpw" + str(i) + ".bend(bendRad, 'r')")
    exec("cpw" + str(i) + ".meander(meanderLen, bendRad, 500,'ll')")
    exec("poly = gdspy.PolygonSet(cpw" + str(i) + ".path.polygons)")
    exec("gdslib.addPolyToCell(poly,device)")
    exec("print(cpw" + str(i) + ".len())")

# BOTTOM RESONATOR ARRAY
f = linspace(4.5E9,4.6E9,7) # Fundamental frequency
l4 = c/sqrt(ereff)/4./f*1E6 # length for lambda/4 resonator
print(l4)

for i in range(0,6):
    totalLength = l4[i]
    openDis = 10
    capDist = 10*(1+i)
    cpwSrtExtend = 200
    bendRad = 100
    meanderLen = totalLength - openDis - capDist - cpwSrtExtend - pi*bendRad
    exec("cpw" + str(i) + " = gdslib.CPWPath(10,5,layer = 6)")
    exec("cpw" + str(i) + ".start([2100 - 750 + 625 + 1250*" + str(i) + ",2500 + 25],'-x')")
    exec("cpw" + str(i) + ".openGap(openDis)")
    exec("cpw" + str(i) + ".straight(capDist)")
    exec("cpw" + str(i) + ".bend(bendRad, 'r')")
    exec("cpw" + str(i) + ".straight(cpwSrtExtend)")
    exec("cpw" + str(i) + ".bend(bendRad, 'r')")
    exec("cpw" + str(i) + ".meander(meanderLen, bendRad, 500,'ll')")
    exec("poly = gdspy.PolygonSet(cpw" + str(i) + ".path.polygons)")
    exec("gdslib.addPolyToCell(poly,device)")
    exec("print(cpw" + str(i) + ".len())")

gdspy.gds_print(deviceName + '.gds', unit=1.0e-6, precision=1.0e-9)

gdspy.LayoutViewer()
