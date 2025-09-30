# 📡 Planetary Position Visualizer

This project is a planetary position calculator and visualizer that lets users compute and display the position of planets (Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune) for a given date and time. It includes both a command-line interface (CLI) and a graphical user interface (GUI).

---------------
Built using:

##🛰️ Skyfield
 – for precise astronomical calculations

🐍 Python

🗃️ MySQL – for logging planetary positions

🎨 PyQt5 + Matplotlib – for an interactive sky map GUI

----------


# 📁 Features




🌐 Compute azimuth, altitude, right ascension (RA), declination (Dec), and distance (AU)

💾 Save results to a MySQL database

🧭 Select observer location (Lat/Lon)

📈 Visualize planet positions on a polar sky map

🖥️ Two interfaces:

CLI (Command Line)

GUI (PyQt5-based)

---------

| CLI                         | GUI                         |
| --------------------------- | --------------------------- |
| ![CLI](assets/cli_demo.png) | ![GUI](assets/gui_demo.png) |


Add your own screenshots to the assets/ folder and update the paths above.

------

🔧 Installation

1. Clone the repository
   git clone https://github.com/your-username/planet-visualizer.git
cd planet-visualizer

2. Install dependencies
   It's recommended to use a virtual environment:

   python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3.Setup MySQL database

   CREATE DATABASE IF NOT EXISTS planet_db;
USE planet_db;

CREATE TABLE IF NOT EXISTS planet_positions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    az_deg DOUBLE,
    alt_deg DOUBLE,
    ra_hours DOUBLE,
    dec_deg DOUBLE,
    distance_au DOUBLE,
    timestamp DATETIME
);

Update your DB credentials in main_cli.py and db_handler.py.
--------

# 💻 Usage
CLI

python main_cli.py

----------


You will be prompted to enter:

Planet name

Date and time (YYYY-MM-DD HH:MM)


Result will be displayed and saved to MySQL.

-------

# GUI

python main_gui.py

--------

# Use dropdowns to:

Select observer location

---------

# Select planet

Choose date/time

Click “Search / Plot” to visualize sky map

---------

# GUI

python main_gui.py
---------

# Use dropdowns to:

Select observer location

Select planet

Choose date/time

Click “Search / Plot” to visualize sky map

-----
## 📦 Project Structure

solarsystem/

├── planet.py         # Planet classes

├── engine.py         # PlanetEngine logic

├── db_handler.py     # MySQL integration

├── gui.py            # GUI logic

main_cli.py           # CLI entry point

main_gui.py           # GUI entry point

requirements.txt

README.md

## 📜 License

This project is open-source and available under the MIT License
----

## 🙌 Credits

# Skyfield
 for astronomical calculations

# PyQt5
 for GUI

# Matplotlib
 for sky plotting

 ---------




