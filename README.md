# 📡🌌 Planetary Sky Position Simulator

The Sky Map Viewer is a Python-based desktop application built with PyQt5 and Matplotlib. It allows users to visualize the real-time positions of planets in the sky from a selected location and time. The application provides detailed astronomical data, including azimuth, altitude, right ascension, declination, and distance for each planet.

This project is ideal for students, astronomy enthusiasts, and anyone interested in exploring planetary positions in a visual, interactive way.


# 🚀 Features

Interactive Sky Map: Displays the positions of planets on a polar coordinate sky map.

City Selection: Choose from multiple global locations to update the observer’s latitude and longitude.

Date & Time Control: Set a custom UTC date and time to view planets’ positions at that moment.

Planet Information Panel: Shows detailed data for the selected planet, including azimuth, altitude, right ascension, declination, and distance.

Visual Alerts: Displays warnings if a planet is below the horizon.

Hidden Bodies List: Provides information on planets that are not currently visible.


# 📚 Libraries Used

The following Python libraries are required:

Library	Purpose
  - PyQt5	         - GUI framework for windows, widgets, layouts, and dialogs
  - Matplotlib	    - Plotting sky maps in polar coordinates
  - Numpy	         - Mathematical operations for angles and coordinates
  - datetime	      - Handling dates and times in UTC
  - pathlib	       - File system paths for images and resources
  - sys	           - System-level operations for application execution
  - timezone	      - Timezone handling for accurate planet positions

Make sure all libraries are installed before running the project.


# 🛠 Usage

Launch the application.

Select your city from the City dropdown menu.

Select a planet from the Body dropdown menu.

Choose the desired UTC Date & Time.

Click the Search / Plot button.

View the planet on the sky map and read detailed information in the info panel.

Access Help or About from the menu bar for instructions or project information.


## 📂 Project Structure

sky-map-viewer/
│
├─ gui.py               # Main application GUI code
├─ solarsystem.py       # PlanetEngine for calculating planetary positions
├─ images/              # Planet images (Mercury.png, Venus.png, etc.)
└─ README.md            # Project documentation

## Team Members 👩‍💻👨‍💻
-Kasun Ranga
-Thiloka Dasanayaka
-Poojana Dinushan
-Sanili Jesmina
-Dilmi Amasha
-Sanjana De Silva
-Navodya Sankalpani






