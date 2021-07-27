#!/usr/bin/env python3
# Fire wx kestrel plotting/comparison script
# Created 15 July 2021 by Ashley Palm <ashleyp0301@tamu.edu>, Sam Gardner <stgardner4@tamu.edu>
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime as dt

rowstodrop1 = 6 #configure this as needed (rows including units of unusable data)
rowstodrop2 = 8 #configure this as needed (rows including units of unusable data)
## Read in files
drop1 = pd.read_csv('D3_FIRE_-_2539642_Jul_23_2021_4_00_00_PM.csv',skiprows=3) # Low sensor
drop2 = pd.read_csv('D3_FIRE_-_2592842_Jul_23_2021_4_08_00_PM.csv',skiprows=3) # High sensor
prt = pd.read_html("Table Display.html")
prt = prt[0]
## Drop requested number of rows from header
drop1 = drop1.drop(range(rowstodrop1))
drop2 = drop2.drop(range(rowstodrop2))
## Drop null values to prevent parsing errors
drop1 = drop1.dropna(how="all")
drop2 = drop2.dropna(how="all")
prt = prt.dropna(how="all")
## As of 17 Jun 2021, the kestrel doesn't correctly format the column headers in the csv export. 
## Every column after "Dew Point" has its header on the first row of data, which leads to pandas referring to them as "Unnamed Column #".
## Since we need teh "Data Type" column, manually fix that. This code may need to be removed if Kestrel ever fixes this or changes their ordering. 
drop1.rename(columns={"Unnamed: 7":"Data Type"}, inplace=True)
drop2.rename(columns={"Unnamed: 7":"Data Type"}, inplace=True)
## Filter to only data that are "point" types -- we aren't interested in snapshot or session data
drop1 = drop1[drop1["Data Type"].str.contains("point")]
drop2 = drop2[drop2["Data Type"].str.contains("point")]

## Convert drop1's "Temperature" column from a pandas series to a python list (easier/faster for loop iteration)
drop1TStrList = drop1["Temperature"].tolist()
drop1TList = list()
## Parse drop1's temperature values (read in by pandas as strings) into floating-point numbers so that matplotlib can properly graph them
for T1Str in drop1TStrList:
    drop1TList.append(float(T1Str))
## Convert drop1's timestamps into a python list... we're doing the same thing we just did with the Temperature data
drop1dtStrList = drop1["FORMATTED DATE_TIME"].tolist()
drop1dtList = list()
## Convert timestamp string to python datetime objects
for dt1Str in drop1dtStrList:
    drop1dtList.append(dt.strptime(dt1Str, "%b %d, %Y %I:%M:%S %p"))

## Now we do all of that parsing, but this time on the drop2 file...
drop2TStrList = drop2["Temperature"].tolist()
drop2TList = list()
for T2Str in drop2TStrList:
    drop2TList.append(float(T2Str))
drop2dtStrList = drop2["FORMATTED DATE_TIME"].tolist()
drop2dtList = list()
for dt2Str in drop2dtStrList:
    drop2dtList.append(dt.strptime(dt2Str, "%b %d, %Y %I:%M:%S %p"))

## And now we do that again but for the prt data
prtdtStrList = prt["Time Stamp"].tolist()
prtdtList = list()
for dtprtStr in prtdtStrList:
    prtdtList.append(dt.strptime(dtprtStr, "%Y-%m-%d %H:%M:%S"))
## Temperature on from the prt sensors reads in as floats and doesn't need parsing
prtTList = prt["low_temp_C_Avg"].tolist()


## Create a matplotlib figure and get a handle "fig"
fig = plt.figure()
## Set the figure size to something readable instead of the default 432px
px = 1/plt.rcParams["figure.dpi"] # plt insists on using inches as the only unit of image size... grrrrrr...
fig.set_size_inches(1920*px, 1080*px)
## Set figure background
fig.set_facecolor("white")
## Get axis handle "ax"
ax = plt.axes()
## Plot drop1's temperature vs datetime onto fig
ax.plot(drop1dtList, drop1TList, "b", label="Kestrel 2539642")
## Plot drop2's temperature vs datetime onto fig
ax.plot(drop2dtList, drop2TList, "orange", label="Kestrel 2592842")
## Plot PRT data
ax.plot(prtdtList, prtTList, "turquoise", label="Platinum Resistance Thermometer (Low)")
## Show Legend
ax.legend()
## Save fig as "test.png" in current directory
fig.savefig("temp.png")

## Calculate difference between high and low kestrels
differenceDTList = list()
differenceTList = list()
for targetDate in drop1dtList:
    if targetDate in drop2dtList:
        drop1TargetTemp = drop1TList[drop1dtList.index(targetDate)]
        drop2TargetTemp = drop2TList[drop2dtList.index(targetDate)]
        diff = drop1TargetTemp - drop2TargetTemp
        differenceDTList.append(targetDate)
        differenceTList.append(diff)

## Plot differences
diffFig = plt.figure()
diffFig.set_size_inches(1920*px, 1080*px)
diffAx = plt.axes()
diffAx.plot(differenceDTList, differenceTList, label="Difference")
diffAx.set_xlabel("Date")
diffAx.set_ylabel("Difference in T, positive = inverstion")
diffFig.savefig("difference.png")

## Print a table
diffTable = pd.DataFrame(data={"Date" : differenceDTList, "Difference" : differenceTList})
print(diffTable)
## Thanks, and gig'em!