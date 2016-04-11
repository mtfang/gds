from math import *
import AutoScripter

pathAutoCAD = "C:\Program Files\Autodesk\AutoCAD 2016"
widthReadout = 4
gapReadout = 4
padWidth = 200
padLength  = 200
launcherLength = 400
launcherWidth  = 350
launcherGap = (launcherWidth - padWidth)/2
launcherRamp = launcherLength - padLength - launcherGap
readoutRadius = 100

widthResonator = 4
gapResonator = 4

readoutHeight = 5000
launcherHeight = 500

meanderSrtLen = 500
meanderRadius = 100

a = AutoScripter.newScript('ReadoutSimple.scr')

# Frame
a.addLayer("Frame", [250,50,50])
a.addRect(base = [0,0], xlen = 10000, ylen = 10000)
#a.convertPolyToRegion("Frame")

# Readout line
a.addLayer("CPW", [50,250,50])
a.launchPadBegin(padWidth, launcherWidth, widthReadout, gapReadout, padLength, launcherRamp, [500,launcherHeight], startAngleRad = pi/2)
a.addCPWStraightLenAng(widthReadout, gapReadout, length = readoutHeight - launcherHeight - launcherLength - readoutRadius, start = a.prevEnd, startAngleRad = a.prevAngleRad)
a.addCPWAngBend(widthReadout, gapReadout, readoutRadius, -90, a.prevEnd, a.prevAngleRad)
a.addCPWStraightLenAng(widthReadout, gapReadout, length = 9000 - 2*readoutRadius - padWidth/2, start = a.prevEnd, startAngleRad = a.prevAngleRad)
a.addCPWAngBend(widthReadout, gapReadout, readoutRadius, -90, a.prevEnd, a.prevAngleRad)
a.addCPWStraightLenAng(widthReadout, gapReadout, length = readoutHeight - launcherHeight - launcherLength - readoutRadius, start = a.prevEnd, startAngleRad = a.prevAngleRad)
a.launchPadEnd(padWidth, launcherWidth, widthReadout, gapReadout, padLength, launcherRamp, a.prevEnd, a.prevAngleRad)

# Resonator Array
for i in range(0,7):
    a.addCPWStraightLenAng(widthResonator, gapResonator, length = meanderSrtLen, start = [1200*i + 1750, readoutHeight - 2*widthResonator - 2*gapResonator], startAngleRad = -pi)
    a.CPWMeander(widthResonator, gapResonator, 8000+i*500, meanderRadius, meanderSrtLen, pi, a.prevEnd, a.prevAngleRad)
    a.addCPWRectGap(widthResonator, gapResonator, gapResonator, a.prevEnd, a.prevAngleRad)
#a.convertPolyToRegion("CPW")
#a.subtractLayers("CPW", "Frame")
#a.convertRegionToPoly("Frame")
a.exportDXF()

a.runScript(pathAutoCAD)
