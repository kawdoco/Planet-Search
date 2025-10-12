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


class MainWindow(QMainWindow):  # QMainWindow to support menu bar
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sky Map Viewer - Planet & Star Tracker")
        #self.setWindowTitle("AstroLocator")
        self.setGeometry(100, 100, 1000, 600)

        self.engine = PlanetEngine()

        self.init_menu()   # Add menu bar
        self.init_ui()     # Setup layout

    def init_menu(self):
        menubar = self.menuBar()

        # Apply dark blue style
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #01161e;
                color: white;
                font-weight: bold;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 10px;
            }
            QMenuBar::item:selected {
                background-color: #124559;
            }
            QMenu {
                background-color: #01161e;
                color: white;
                border: 1px solid #124559;
            }
            QMenu::item:selected {
                background-color: #124559;
            }
        """)

        # File menu
        file_menu = menubar.addMenu("Exit")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_action = QAction("How to use", self)
        help_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(help_action)

        # about menu
        #about_menu = menubar.addMenu("About")
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
        layout = QVBoxLayout()

        # Top controls
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Observer latitude:"))
        self.lat_cb = QComboBox()
        self.lat_cb.addItem("0.0", 0.0)
        self.lat_cb.addItem("6.9271 (Colombo)", 6.9271)
        self.lat_cb.addItem("51.5074 (London)", 51.5074)
        controls.addWidget(self.lat_cb)

        controls.addWidget(QLabel("longitude:"))
        self.lon_cb = QComboBox()
        self.lon_cb.addItem("0.0", 0.0)
        self.lon_cb.addItem("79.8612 (Colombo)", 79.8612)
        self.lon_cb.addItem("-0.1278 (London)", -0.1278)
        controls.addWidget(self.lon_cb)

        controls.addWidget(QLabel("Body:"))
        self.body_cb = QComboBox()
        for b in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]:
            self.body_cb.addItem(b)
        controls.addWidget(self.body_cb)

        controls.addWidget(QLabel("DateTime (UTC):"))
        self.dt_edit = QDateTimeEdit(QDateTime.currentDateTimeUtc())
        self.dt_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.dt_edit.setCalendarPopup(True)
        controls.addWidget(self.dt_edit)

        self.search_btn = QPushButton("Search / Plot")
        self.search_btn.clicked.connect(self.on_search)
        controls.addWidget(self.search_btn)

        layout.addLayout(controls)

        # Main content area
        main_content = QHBoxLayout()

        # Sky canvas
        self.canvas = SkyCanvas(self)
        main_content.addWidget(self.canvas, stretch=3)

        # Info panel
        self.info_label = QLabel("Planet details will appear here")
        self.info_label.setWordWrap(True)
        self.info_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.info_label.setMinimumWidth(250)
        self.info_label.setStyleSheet("""
            background-color: #01161e;
            color: white;
            border: 1px solid #124559;
            border-radius: 6px;
            padding: 10px;
        """)
        main_content.addWidget(self.info_label, stretch=1)

        layout.addLayout(main_content)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def on_search(self):
        lat = float(self.lat_cb.currentData())
        lon = float(self.lon_cb.currentData())
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
            info = f"""
            <div style="font-family: Times New Roman; font-size: 12pt; color: #222;">
                <h1 style="color:#1AB0A3; margin-bottom:4px;">{sel_body}</h1>
                <p style="color:#fff;"><b>UTC:</b> {dt.isoformat()}</p>
                <table  style="border-spacing: 6px; color:#fff;">
                    <tr><td><b>Azimuth:</b></td><td>{chosen['az_deg']:.2f}°</td></tr>
                    <tr><td><b>Altitude:</b></td><td>{chosen['alt_deg']:.2f}°</td></tr>
                    <tr><td><b>Right Ascension:</b></td><td>{chosen['ra_hours']:.4f} h</td></tr>
                    <tr><td><b>Declination:</b></td><td>{chosen['dec_deg']:.4f}°</td></tr>
                    <tr><td><b>Distance:</b></td><td>{chosen['distance_au']:.4f} AU</td></tr>
                </table>
            """

            if chosen['alt_deg'] <= 0:
                info += """
                <p style="color:red; margin-top:6px;">
                    <br>⚠️ Not visible on sky map because it is below the horizon.<br>
                </p>
                """

            if hidden_reasons:
                info += "<h2 style='margin-top:10px; color:#CFE67E;'>Other Hidden Bodies</h2>"
                info += "<ul style='color:white;'>"
                for reason in hidden_reasons:
                    info += f"<li>{reason}</li>"
                info += "</ul>"

            info += "</div>"
            self.info_label.setText(info)

        except Exception as e:
            self.info_label.setText(f"<span style='color:red'>Error: {str(e)}</span>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
