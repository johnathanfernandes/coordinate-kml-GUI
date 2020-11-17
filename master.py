#--------------- Imports
import simplekml
from polycircles import polycircles
import tkinter
from tkinter import ttk, Tk, Label, Button, Entry, Listbox
import math

#--------------- Define GUI

root = Tk()
root.title("Coordinates to .kml generator")
root.geometry("550x300")

#--------------- Define functions

def quit(): # closes app
    global root
    root.quit()
    root.destroy()

def texttocoord(text): # Converts coordinate text to numbers
    textlist = text.split()
    
    latdeg = float(textlist[0][0:2])
    latmin = float(textlist[0][2:4])
    latsec = float(textlist[0][4:-1])
    lat = latdeg + (latmin/60) + (latsec/3600)
    if textlist[0][-1] == "S":
        lat = lat*-1
    
    longdeg = float(textlist[1][0:3])
    longmin = float(textlist[1][3:5])
    longsec = float(textlist[1][5:-1])
    long = longdeg + (longmin/60) + (longsec/3600)
    if textlist[1][-1] == "W":
        long = long*-1
    
    coord = (long,lat)
    return coord
    
def savecoords(): # Add coordinates to list for polygon
    notam = str(PolygonCoordEntry.get())
    boundary.append(texttocoord(notam))
    PolygonCurrentList.insert(tkinter.END,notam)

def reset(): # Reset lists
    PolygonCurrentList.delete(0,tkinter.END)
    boundary.clear()
    StatusLabel["text"] = "Status: Reset" 
    
def generatepolygon(): # Generate polygon from list
    kml = simplekml.Kml()
    boundary.append(boundary[0])
    pol = kml.newpolygon(name = PolygonNameEntry.get())
    pol.outerboundaryis = boundary
    pol.style.linestyle.color = simplekml.Color.green
    pol.style.linestyle.width = 5
    pol.style.polystyle.color = simplekml.Color.changealphaint(200, simplekml.Color.green)
    kml.save(PolygonNameEntry.get() +".kml")
    StatusLabel["text"] = "Status: kml file generated"    

def generatecircle(): # Generate circle from coordinates and radius
    kml = simplekml.Kml()
    
    notam = str(CircleCoordEntry.get())
    coord = texttocoord(notam)
    
    polycircle = polycircles.Polycircle(latitude=float(coord[1]),
                                    longitude=float(coord[0]),
                                    radius=float(CircleRadiusEntry.get()),
                                    number_of_vertices=math.ceil(float(CircleRadiusEntry.get())/2))
    kml = simplekml.Kml()
    pol = kml.newpolygon(name=CircleNameEntry.get(),
                                             outerboundaryis=polycircle.to_kml())
    pol.style.polystyle.color = \
            simplekml.Color.changealphaint(200, simplekml.Color.green)
    kml.save(CircleNameEntry.get() +".kml")
    StatusLabel["text"] = "Status: kml file generated" 

#--------------- Main GUI code

tabControl = ttk.Notebook(root)

Polygon = ttk.Frame(tabControl)
tabControl.add(Polygon, text='Polygon')

Circle = ttk.Frame(tabControl)
tabControl.add(Circle, text='Circle')

tabControl.grid(column = 0, row = 0)

#--------------- GUI for polygon

NameLabel = Label(Polygon, text = "Name: ")
NameLabel.grid(column = 0, row = 1)

PolygonNameEntry = Entry(Polygon)
PolygonNameEntry.grid(column = 1, row = 1)

PolygonCoordLabel = Label(Polygon, text = "Enter coordinates: ")
PolygonCoordLabel.grid(column = 0, row = 2)

PolygonCoordEntry = Entry(Polygon)
PolygonCoordEntry.grid(column = 1, row = 2)

boundary = []

PolygonAddButton = Button(Polygon, text="Add point", command=savecoords)
PolygonAddButton.grid(column = 0, row = 3)

PolygonCurrentLabel = Label(Polygon, text = "Current points: ")
PolygonCurrentLabel.grid(column = 2, row = 1)

PolygonCurrentList = Listbox(Polygon)
PolygonCurrentList.grid(column = 2, row = 2, columnspan = 3, rowspan = 3)

PolygonGenerate = Button(Polygon, text="Generate kml file", command=generatepolygon)
PolygonGenerate.grid(column = 0, row = 4)

#--------------- GUI for circle 

CircleNameLabel = Label(Circle, text = "Name: ")
CircleNameLabel.grid(column = 0, row = 1)

CircleNameEntry = Entry(Circle)
CircleNameEntry.grid(column = 1, row = 1)

CircleCoordLabel = Label(Circle, text = "Enter coordinates: ")
CircleCoordLabel.grid(column = 0, row = 2)

CircleCoordEntry = Entry(Circle)
CircleCoordEntry.grid(column = 1, row = 2)

CircleRadiusLabel = Label(Circle, text = "Enter radius (in m): ")
CircleRadiusLabel.grid(column = 0, row = 3)

CircleRadiusEntry = Entry(Circle)
CircleRadiusEntry.grid(column = 1, row = 3)

CircleGenerate = Button(Circle, text="Generate kml file", command=generatecircle)
CircleGenerate.grid(column = 0, row = 4)

#--------------- Shared GUI buttons

StatusLabel = Label(root, text = "Status: ")
StatusLabel.grid(column = 1, row = 5)

QuitButton = Button(root, text="Quit", command=quit)
QuitButton.grid(column = 0, row = 2)

ResetButton = Button(root, text="Reset", command=reset)
ResetButton.grid(column = 0, row = 1)

root.mainloop()