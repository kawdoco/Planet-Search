import sys                      
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QDateTimeEdit, QMessageBox,
    QFrame, QAction
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDateTime, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime, timezone
import numpy as np
from pathlib import Path
from solarsystem import PlanetEngine


# ---------------- SKY MAP CANVAS ----------------
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


# ---------------- MAIN WINDOW ----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Planet Explorer")
        self.setGeometry(100, 100, 1000, 600)

        self.engine = PlanetEngine()

        self.init_menu()
        self.show_home_page()  # start with home page

    # -------- MENU BAR --------
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

    # -------- HOME PAGE --------
    def show_home_page(self):
        home_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Welcome to Planet Explorer!")
        title.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")

        subtitle = QLabel("Track planets, explore the sky, and see their details.")
        subtitle.setStyleSheet("color: #CCCCCC; font-size: 16px; margin-bottom: 30px;")

        search_btn = QPushButton("🔭  Search Planet")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #2979FF;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 12px 30px;
                border-radius: 10px;
            }
            QPushButton:hover { background-color: #1E88E5; }
        """)
        search_btn.clicked.connect(self.show_planet_page)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(search_btn)

        home_widget.setLayout(layout)
        home_widget.setStyleSheet("background-color: #000814;")

        self.setCentralWidget(home_widget)

    # -------- PLANET PAGE --------
    def show_planet_page(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Home icon
        home_btn = QPushButton("🏠 Home")
        home_btn.setStyleSheet("""
            QPushButton {
                background-color: #124559;
                color: white;
                border-radius: 8px;
                padding: 6px 15px;
            }
            QPushButton:hover { background-color: #1A6C7A; }
        """)
        home_btn.clicked.connect(self.show_home_page)

        main_layout.addWidget(home_btn, alignment=Qt.AlignLeft)

        # --- Controls layout ---
        controls = QHBoxLayout()

        controls.addWidget(QLabel("Select City:"))
        self.city_cb = QComboBox()
        self.cities = {
            "Colombo": (6.9271, 79.8612),
            "Kandy": (7.2964, 80.6350),
            "Galle": (6.0360, 79.9179),
            "Jaffna": (9.6606, 80.0140),
            "Trincomalee": (8.5850, 81.2301),
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

        default_city = "Colombo"
        self.city_cb.setCurrentText(default_city)
        self.lat, self.lon = self.cities[default_city]
        self.city_cb.currentTextChanged.connect(self.update_coordinates)
        controls.addWidget(self.city_cb)

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

        main_layout.addLayout(controls)

        # --- Main content area ---
        main_content = QHBoxLayout()
        self.canvas = SkyCanvas(self)
        main_content.addWidget(self.canvas, stretch=3)

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

    # -------- OTHER FUNCTIONS --------
    def update_coordinates(self, city_name):
        self.lat, self.lon = self.cities.get(city_name, (0.0, 0.0))

    def on_search(self):
        try:
            lat = self.lat
            lon = self.lon
            qdt = self.dt_edit.dateTime().toUTC()
            dt = datetime(qdt.date().year(), qdt.date().month(), qdt.date().day(),
                          qdt.time().hour(), qdt.time().minute(), qdt.time().second(),
                          tzinfo=timezone.utc)
            sel_body = self.body_cb.currentText()
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

            image_path = f"images/{sel_body}.png"
            if Path(image_path).exists():
                image_html = f"""
                <div style="text-align:center; margin-bottom:15px;">
                    <img src="{image_path}" width="150" height="150">
                </div>
                """
            else:
                image_html = "<p style='color:#CFE67E; text-align:center; margin-bottom:15px;'>Image not available</p>"

            details_html = f"""
            <h1 style="color:#1AB0A3; margin-bottom:10px; text-align:center;">{sel_body}</h1>
            <p><b>UTC:</b> {dt.isoformat()}</p>
            <table style="border-spacing: 6px; color:#fff;">
                <tr><td><b>Azimuth:</b></td><td>{chosen['az_deg']:.2f}°</td></tr>
                <tr><td><b>Altitude:</b></td><td>{chosen['alt_deg']:.2f}°</td></tr>
                <tr><td><b>Right Ascension:</b></td><td>{chosen['ra_hours']:.4f} h</td></tr>
                <tr><td><b>Declination:</b></td><td>{chosen['dec_deg']:.4f}°</td></tr>
                <tr><td><b>Distance:</b></td><td>{chosen['distance_au']:.4f} AU</td></tr>
            </table>
            """

            warning_html = ""
            if chosen['alt_deg'] <= 0:
                warning_html = "<p style='color:red;'>⚠️ Not visible (below horizon).</p>"

            hidden_html = ""
            if hidden_reasons:
                hidden_html += "<h2 style='color:#CFE67E;'>Other Hidden Bodies</h2><ul>"
                for reason in hidden_reasons:
                    hidden_html += f"<li>{reason}</li>"
                hidden_html += "</ul>"

            info = f"<div style='color:white;'>{image_html}{details_html}{warning_html}{hidden_html}</div>"
            self.info_label.setText(info)

        except Exception as e:
            self.info_label.setText(f"<span style='color:red'>Error: {str(e)}</span>")

    def show_help_dialog(self):
        QMessageBox.information(self, "How to Use",
            "Select your city, pick a planet, and click 'Search / Plot' to view its position on the sky map.")

    def show_about_dialog(self):
        QMessageBox.information(self, "About",
            "🌌 Planet Explorer\nCreated by BCI Campus\nVersion 1.0\n2025")


# -------- MAIN --------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

