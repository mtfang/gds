from numpy import *
import gdspy
import gdslib
import os
deviceName = '2016Mar29_Resonators'
device = gdspy.Cell(deviceName)

print(os.chdir("C:/Users/Michael/Dropbox/GitHub/PainterQubits/devMichael/AutoCAD/gdspy"))
# FREQUENCY DESIGN
# [1] Coplanar Waveguide Circuits, Components, and Systems by Rainee Simons
c = 3E8;
er = 11.9 # Substrate dielectric constant
ereff = (1+er)/2; # [1] Eq. 2.30


# BOUNDARY DEFINITIONS
# Boundary of section of chip containing features
device.add(gdspy.Rectangle((0, 0), (10000 , 5000), layer = 1))

# Boundary of the entire 1 cm chip
device.add(gdspy.Rectangle((0, 0), (10000 , 10000), layer = 2))

# Approximate clip placement area
device.add(gdspy.Rectangle((2500, 7000), (7500 , 10000), layer = 3))

# FEEDLINE
cpwfeed = gdslib.CPWPath(300,150,layer = 5, cellName = device)
cpwfeed.start([1125 + 150,100+50],'+y')
cpwfeed.openGapFillet(150,'beg')
cpwfeed.straight(250)
cpwfeed.straight(250, widthEnd = 10, gapEnd = 5)
cpwfeed.straight(3500)
cpwfeed.bend(250, 'r')
cpwfeed.straight(2000)
cpwfeed.bend(250, 'r')
cpwfeed.straight(3000)
cpwfeed.bend(250, 'l')
cpwfeed.straight(2000)
cpwfeed.bend(250, 'l')
cpwfeed.straight(3000)
cpwfeed.bend(250, 'r')
cpwfeed.straight(1950)
cpwfeed.bend(250, 'r')
cpwfeed.straight(3500)
cpwfeed.straight(250, widthEnd = 300, gapEnd = 150)
cpwfeed.straight(250)
cpwfeed.openGapFillet(150,'end')
cpwfeed.end()



f = linspace(6E9,6.05E9,9) # Fundamental frequency
l4 = c/sqrt(ereff)/4./f*1E6 # length for lambda/4 resonator
print(l4)

pts = 9
dWidth = 5 # Change in CPW width
dGap = dWidth/2 # Change in CPW gap
w0 = 5
g0 = w0/2
widths = linspace(w0, w0 + dWidth*(pts - 1), pts)
gaps = linspace(g0, g0 + dGap*(pts - 1), pts)
print(widths)
print(gaps)
# 3X3 Resonator Array
for i in range(0,3):
    for j in range(0,3):
        idx = 3*i + j
        totalLength = l4[idx]
        openDis = gaps[idx]
        capDist = 50
        constantOffset = 15
        distOffset = widths[idx]/2 + gaps[idx] + constantOffset + dWidth*idx
        print(distOffset)
        cpwSrtExtend = 200
        bendRad = 150
        meanderLen = totalLength - openDis - capDist - cpwSrtExtend - pi*bendRad
        cpw = gdslib.CPWPath(widths[idx],gaps[idx],layer = 6, cellName = device)
        cpw.start([1125 + 150 + distOffset + 2500*i,1900  + 1100*j],'+y')
        cpw.openGap(openDis)
        cpw.straight(capDist)
        cpw.bend(bendRad, 'r')
        cpw.straight(cpwSrtExtend)
        cpw.bend(bendRad, 'r')
        cpw.meander(meanderLen, bendRad, 500,'ll')
        cpw.end()


# DEVICE LABEL
deviceText = gdspy.Text(deviceName, 250,
                         (3000,500), layer=4)
device.add(deviceText)

gdspy.LayoutViewer()

gdspy.gds_print(deviceName + '.gds', unit=1.0e-6, precision=1.0e-9)
