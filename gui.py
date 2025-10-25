import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QDateTimeEdit, QMessageBox,
    QFrame, QAction
)
from PyQt5.QtCore import QDateTime, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime, timezone
import numpy as np
from pathlib import Path
from solarsystem import PlanetEngine


class SkyCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5, 5))
        super().__init__(fig)
        self.ax = fig.add_subplot(111, polar=True)
        self.ax.set_theta_zero_location("N")
        self.ax.set_theta_direction(-1)
        self.ax.set_rlim(90, 0)

    def plot_bodies(self, data_list):
        self.ax.clear()
        self.ax.set_theta_zero_location("N")
        self.ax.set_theta_direction(-1)
        self.ax.set_rlim(90, 0)
        for item in data_list:
            az = np.deg2rad(item['az_deg'])
            alt = item['alt_deg']
            label = item['name']
            self.ax.scatter(az, 90 - alt, s=50)
            self.ax.text(az, 90 - alt, " " + label)
        self.ax.set_title("Sky view (azimuth=N=0°, radius = 90°-altitude)")
        self.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sky Map Viewer - Planet & Star Tracker")
        self.setGeometry(100, 100, 1000, 600)

        self.engine = PlanetEngine()

        self.init_menu()
        self.init_ui()

    def init_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar { background-color: #01161e; color: white; font-weight: bold; }
            QMenuBar::item { background-color: transparent; padding: 4px 10px; }
            QMenuBar::item:selected { background-color: #124559; }
            QMenu { background-color: #01161e; color: white; border: 1px solid #124559; }
            QMenu::item:selected { background-color: #124559; }
        """)

        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Help")
        help_action = QAction("How to Use", self)
        help_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(help_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def show_help_dialog(self):
        QMessageBox.information(
            self,
            "How to use",
            """🌌 Select your observing location, then choose the planet you want to view.
The system will display a sky map showing the planet’s current position along with detailed information.
If a planet does not appear on the map, check the "Other Hidden Bodies" list to see if it is below the horizon.
You can change your location at any time to update the sky view."""
        )

    def show_about_dialog(self):
        QMessageBox.information(
            self,
            "About",
            "🌌 Sky Map Viewer\nCreated by BCI Campus\nVersion 1.0\n2025"
        )

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # --- Controls layout ---
        controls = QHBoxLayout()

        # City selection
        controls.addWidget(QLabel("Select City:"))
        self.city_cb = QComboBox()
        self.cities = {
            
            "Colombo": (6.9271, 79.8612),
            "Kandy": (7.2964 , 80.6350),
            "Galle":(6.0360, 79.9179),
            "Jaffna":(9.6606, 80.0140),
            "Trincomalee":(8.5850, 81.2301),
            "Delhi": (28.6333, 77.2167),
            "Mumbai": (19.0833, 72.8667),
            "Kolkata": (22.5667, 88.3667),
            "Chennai": (13.0833, 80.2833),
            "London": (51.5000, -0.1000),
            "Birmingham": (52.4000, -1.9000),
            "Leeds": (53.8000, -1.5000),
            "Liverpool": (53.4000, -3.0000),
            "Bristol": (51.5000, -2.6000),
            "Manchester": (53.5000, -2.3000),



        }
        for city in self.cities:
            self.city_cb.addItem(city)

        # Default selection
        default_city = "Colombo"
        self.city_cb.setCurrentText(default_city)
        self.lat, self.lon = self.cities[default_city]

        self.city_cb.currentTextChanged.connect(self.update_coordinates)
        controls.addWidget(self.city_cb)

        # Body selection
        controls.addWidget(QLabel("Body:"))
        self.body_cb = QComboBox()
        for b in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]:
            self.body_cb.addItem(b)
        controls.addWidget(self.body_cb)

        # DateTime selection
        controls.addWidget(QLabel("DateTime (UTC):"))
        self.dt_edit = QDateTimeEdit(QDateTime.currentDateTimeUtc())
        self.dt_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.dt_edit.setCalendarPopup(True)
        controls.addWidget(self.dt_edit)

        # Search button
        self.search_btn = QPushButton("Search / Plot")
        self.search_btn.clicked.connect(self.on_search)
        controls.addWidget(self.search_btn)

        main_layout.addLayout(controls)

        # --- Main content area ---
        main_content = QHBoxLayout()

        # Sky canvas
        self.canvas = SkyCanvas(self)
        main_content.addWidget(self.canvas, stretch=3)

        # Info panel
        self.info_label = QLabel("Planet details will appear here")
        self.info_label.setWordWrap(True)
        self.info_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.info_label.setMinimumWidth(300)
        self.info_label.setStyleSheet("""
            background-color: #01161e;
            color: white;
            border: 1px solid #124559;
            border-radius: 6px;
            padding: 10px;
        """)
        self.info_label.setAlignment(Qt.AlignTop)
        main_content.addWidget(self.info_label, stretch=1)

        main_layout.addLayout(main_content)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Initialize coordinates
        self.lat = 0.0
        self.lon = 0.0

    def update_coordinates(self, city_name):
        """Update latitude and longitude based on city selection."""
        self.lat, self.lon = self.cities.get(city_name, (0.0, 0.0))
        print(f"Selected city: {city_name}, Latitude: {self.lat}, Longitude: {self.lon}")



    def on_search(self):
        lat = self.lat
        lon = self.lon
        qdt = self.dt_edit.dateTime().toUTC()
        dt = datetime(
            qdt.date().year(), qdt.date().month(), qdt.date().day(),
            qdt.time().hour(), qdt.time().minute(), qdt.time().second(),
            tzinfo=timezone.utc
        )
        sel_body = self.body_cb.currentText()

        try:
            bodies = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
            data = []
            hidden_reasons = []

            for b in bodies:
                pos = self.engine.body_position(b, observer_latlon=(lat, lon), when=dt)
                pos['name'] = b
                if pos['alt_deg'] > 0:
                    data.append(pos)
                else:
                    hidden_reasons.append(f"{b} is below the horizon at this time.")

            self.canvas.plot_bodies(data)
            chosen = self.engine.body_position(sel_body, observer_latlon=(lat, lon), when=dt)

            # Planet image
            image_path = f"images/{sel_body}.png"
            if Path(image_path).exists():
                image_html = f"""
                <div style="text-align:center; margin-bottom:15px;">
                    <img src="{image_path}" width="150" height="150">
                </div>
                """
            else:
                image_html = "<p style='color:#CFE67E; text-align:center; margin-bottom:15px;'>Image not available</p>"

            # Planet details HTML
            details_html = f"""
            <h1 style="color:#1AB0A3; margin-bottom:10px; text-align:center;">{sel_body}<br></h1>
            <p style="margin-bottom:10px;"><b>UTC:</b> {dt.isoformat()}</p>
            <table style="border-spacing: 6px; color:#fff; margin-bottom:10px;">
                <tr><td><b>Azimuth:</b></td><td>{chosen['az_deg']:.2f}°</td></tr>
                <tr><td><b>Altitude:</b></td><td>{chosen['alt_deg']:.2f}°</td></tr>
                <tr><td><b>Right Ascension:</b></td><td>{chosen['ra_hours']:.4f} h</td></tr>
                <tr><td><b>Declination:</b></td><td>{chosen['dec_deg']:.4f}°</td></tr>
                <tr><td><b>Distance:</b></td><td>{chosen['distance_au']:.4f} AU</td></tr>
            </table>
            """

            # Warning if planet is below horizon
            warning_html = ""
            if chosen['alt_deg'] <= 0:
                warning_html = """
                <p style="color:red; margin-top:10px; margin-bottom:10px;">
                    ⚠️ Not visible on sky map because it is below the horizon.
                </p>
                """

            # Hidden bodies
            hidden_html = ""
            if hidden_reasons:
                hidden_html += "<h2 style='margin-top:15px; color:#CFE67E;'><br>Other Hidden Bodies</h2>"
                hidden_html += "<ul style='color:white; margin-bottom:10px;'>"
                for reason in hidden_reasons:
                    hidden_html += f"<li style='margin-bottom:5px;'>{reason}</li>"
                hidden_html += "</ul>"

            # Combine all HTML
            info = f"""
            <div style="font-family: Times New Roman; font-size: 12pt; color: #fff;">
                {image_html}
                {details_html}
                {warning_html}
                {hidden_html}
            </div>
            """

            self.info_label.setText(info)

        except Exception as e:
            self.info_label.setText(f"<span style='color:red'>Error: {str(e)}</span>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
