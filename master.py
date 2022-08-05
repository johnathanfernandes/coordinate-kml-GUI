import simplekml  # Generate kml files
from polycircles import polycircles  # Convert circles to kml compatible polygons
import pandas as pd  # DAta manipulation
from tkinter import Tk, Button, Label  # GUI components
import re  # Regular expressions for text searching
from tkinter.scrolledtext import ScrolledText  # GUI components
import datetime  # Get current date and time for file name


def create():  # Main driver function
    rawtext = str(st.get("1.0", "end-1c"))
    data = rawtext.replace("\n", " ")  # Join lines
    data = data.replace("  ", " ")  # Remove multiple spaces

    # Define text search terms
    circle_text = re.compile(
        r" E\)(.*?)(AREA CIRCLE WITH RADIUS) ([\d]*[\.][\d]*|[\d]*) (M|NM|KM) (CENTERED ON) (([0-9]*[\.][0-9]+)|([0-9]*))(N |S )(([0-9]*[\.][0-9]+)|([0-9]*))(W|E)"
    )
    poly_text = re.compile(
        r" E\)(.*?)(AREA BOUNDED BY LINES JOINING:((( [0-9]*[\.][0-9]+)|( [0-9]*))(N|S)(( [0-9]*[\.][0-9]+)|( [0-9]*))(W|E))*)"
    )

    # Search using regular expressions
    circles = pd.DataFrame(re.findall(circle_text, data))  # Circles
    polygons = pd.DataFrame(re.findall(poly_text, data))  # Polygons

    if len(circles) != 0:
        circles.drop(circles.columns[[6, 7, 10, 11]], axis=1, inplace=True)
        circle_list = circles.apply(process_circles, axis=1, result_type="expand")
        circle_list.columns = ["Event name", "Latitude", "Longitude", "Radius (m)"]

        for idx, circle in circle_list.iterrows():
            polycircle = polycircles.Polycircle(
                latitude=circle["Latitude"],
                longitude=circle["Longitude"],
                radius=circle["Radius (m)"],
                number_of_vertices=round(circle["Radius (m)"] / 2) + 1,
            )
            pol = kml.newpolygon(
                name=circle["Event name"], outerboundaryis=polycircle.to_kml()
            )
            pol.style.polystyle.color = simplekml.Color.changealphaint(
                200, simplekml.Color.green
            )

    if len(polygons) != 0:
        polygons = polygons.iloc[:, 0:2]
        polygon_list = polygons.apply(process_polygons, axis=1, result_type="expand")
        polygon_list.columns = ["Event name", "Locations"]

        for idx, polygon in polygon_list.iterrows():
            pol = kml.newpolygon(name=polygon["Event name"])
            pol.outerboundaryis = polygon["Locations"]
            pol.style.linestyle.color = simplekml.Color.green
            pol.style.linestyle.width = 5
            pol.style.polystyle.color = simplekml.Color.changealphaint(
                200, simplekml.Color.green
            )

    ct = datetime.datetime.now()
    filename = str(f"{ct.year}_{ct.month}_{ct.day}_{ct.hour}_{ct.minute}_{ct.second}")

    status = str(
        f"kml generated \n {len(circles)} Circles \n {len(polygons)} Polygons \n Filename: {filename}.kml"
    )
    label = Label(root, text=status)
    label.grid(column=1, row=1)
    kml.save(f"{filename}.kml")


def process_circles(circle):

    # Convert latitude from standard NOTAM notation to map form
    lat_deg = float(circle[5][0:2])
    lat_min = float(circle[5][2:4])
    lat_sec = float(circle[5][4:])
    lat = lat_deg + (lat_min / 60) + (lat_sec / 3600)

    # Convert longitude
    long_deg = float(circle[9][0:3])
    long_min = float(circle[9][3:5])
    long_sec = float(circle[9][5 : len(circle[9])])
    longi = long_deg + (long_min / 60) + (long_sec / 3600)

    # Convert NM and KM to M if present
    if circle[3] == "NM":
        rad = float(circle[2]) * 1852.001
    elif circle[3] == "KM":
        rad = float(circle[2]) * 1000
    else:
        rad = float(circle[2])

    # Define event name
    name = str(re.sub("(.*?)E\)", "", circle[0]) + " ".join(circle[1:]))

    return [name, lat, longi, rad]


def process_polygons(polygon):

    # Keep only coordinate text
    coords_list = polygon[1][30:].split()
    coordinate_pairs = []

    # Iterate through coordinates and split into pairs
    for i in range(0, len(coords_list), 2):

        # Convert latitude
        lat_deg = float(coords_list[i][0:2])
        lat_min = float(coords_list[i][2:4])
        lat_sec = float(coords_list[i][4:-1])
        lat = lat_deg + (lat_min / 60) + (lat_sec / 3600)

        # Convert longitude
        long_deg = float(coords_list[i + 1][0:3])
        long_min = float(coords_list[i + 1][3:5])
        long_sec = float(coords_list[i + 1][5:-1])
        longi = long_deg + (long_min / 60) + (long_sec / 3600)

        coordinate_pairs.append([longi, lat])

    name = str(re.sub("(.*?)E\)", "", polygon[0]) + polygon[1])

    return [name, coordinate_pairs]


kml = simplekml.Kml()  # Initialize kml file

# Initialize GUI
root = Tk()
root.title("Coordinate to .kml generator 2.0")
root.geometry("550x300")

# Define GUI
st = ScrolledText(root, width=20, height=3)
st.grid(column=0, row=0)

Button(root, text="Generate kml file", command=create).grid(column=1, row=0)

root.mainloop()
