import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QDateTimeEdit, QMessageBox,
    QFrame, QAction
)
from PyQt5.QtGui import QIcon, QPixmap
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
        self.setGeometry(100, 100, 1200, 700)
        self.engine = PlanetEngine()
        self.current_theme = "dark"
        self._text_color = "white"
        self._highlight_color = "#1AB0A3"
        self._warning_color = "red"
        self.init_menu()
        self.show_home_page()

    # -------- MENU BAR --------
    def init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        home_menu = menubar.addMenu("Home")
        home_action = QAction("Go Home", self)
        home_action.triggered.connect(self.show_home_page)
        home_menu.addAction(home_action)

        help_menu = menubar.addMenu("Help")
        help_action = QAction("How to Use", self)
        help_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(help_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        self.theme_menu = menubar.addMenu("Mode")
        self.dark_action = QAction("Dark Mode ✓", self)
        self.dark_action.triggered.connect(self.set_dark_mode)
        self.light_action = QAction("Light Mode", self)
        self.light_action.triggered.connect(self.set_light_mode)
        self.theme_menu.addAction(self.dark_action)
        self.theme_menu.addAction(self.light_action)

    # -------- THEME FUNCTIONS --------
    def apply_theme(self):
        if self.current_theme == "dark":
            bg_color = "#01161e"
            text_color = "white"
            highlight_color = "#1AB0A3"
            menu_style = """
                QMenuBar { background-color: #01161e; color: white; font-weight: bold; }
                QMenuBar::item:selected { background-color: #124559; }
                QMenu { background-color: #01161e; color: white; border: none; }
            """
            palette = f"""
                QMainWindow {{ background-color: {bg_color}; color: {text_color}; }}
                QLabel {{ color: {text_color}; border: none; }}
                QPushButton {{
                    background-color: #124559;
                    color: white;
                    border: none;
                    border-radius: 8px;
                }}
                QPushButton:hover {{ background-color: #1a6b7b; }}
                QComboBox, QDateTimeEdit {{
                    background-color: #124559;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 6px;
                }}
            """
            self.dark_action.setText("Dark Mode ✓")
            self.light_action.setText("Light Mode")
        else:
            bg_color = "#f5f5f5"
            text_color = "black"
            highlight_color = "#124559"
            menu_style = """
                QMenuBar { background-color: #ffffff; color: black; font-weight: bold; }
                QMenuBar::item:selected { background-color: #aec3b0; }
                QMenu { background-color: #ffffff; color: black; border: 1px solid #ccc; }
            """
            palette = f"""
                QMainWindow {{ background-color: {bg_color}; color: {text_color}; }}
                QLabel {{ color: {text_color}; border: none; }}
                QPushButton {{
                    background-color: #598392;
                    color: white;
                    border: none;
                    border-radius: 8px;
                }}
                QPushButton:hover {{ background-color: #476f77; }}
                QComboBox, QDateTimeEdit {{
                    background-color: #aec3b0;
                    color: black;
                    border: none;
                    padding: 5px;
                    border-radius: 6px;
                }}
            """
            self.dark_action.setText("Dark Mode")
            self.light_action.setText("Light Mode ✓")

        self.setStyleSheet(palette)
        self.menuBar().setStyleSheet(menu_style)
        self._text_color = text_color
        self._highlight_color = highlight_color

        if hasattr(self, 'info_label'):
            self.info_label.setStyleSheet(f"color: {text_color}; padding: 10px; border: none;")

    def set_dark_mode(self):
        self.current_theme = "dark"
        self.apply_theme()

    def set_light_mode(self):
        self.current_theme = "light"
        self.apply_theme()

    # -------- HOME PAGE --------
    def show_home_page(self):
        home_widget = QWidget()
        layout = QVBoxLayout(home_widget)
        layout.setAlignment(Qt.AlignCenter)

        self.bg_label = QLabel(home_widget)
        pixmap = QPixmap("images/home6.jpg")
        self.bg_label.setPixmap(pixmap)
        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.lower()

        title = QLabel("Welcome to Planet Explorer!")
        title.setStyleSheet("font-size: 48px; font-weight: bold; color: white; border: none;")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Track planets, explore the sky, and see their details.")
        subtitle.setStyleSheet("font-size: 18px; color: white; border: none; margin-bottom: 30px;")
        subtitle.setAlignment(Qt.AlignCenter)

        # ✅ Smaller Home Page button
        search_btn = QPushButton("🔭  Search Planet")
        search_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 8px;
                background-color: #124559;
                color: white;
            }
            QPushButton:hover {
                background-color: #1a6b7b;
            }
        """)
        search_btn.clicked.connect(self.show_planet_page)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(search_btn)
        home_widget.resizeEvent = self.home_resize_event

        self.setCentralWidget(home_widget)
        self.apply_theme()

    def home_resize_event(self, event):
        if hasattr(self, 'bg_label'):
            self.bg_label.setGeometry(0, 0, event.size().width(), event.size().height())

    # -------- PLANET PAGE --------
    def show_planet_page(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        controls = QHBoxLayout()

        controls.addWidget(QLabel("Select City:"))
        self.city_cb = QComboBox()
        self.cities = {
            "Colombo": (6.9271, 79.8612),
            "Kandy": (7.2964, 80.6350),
            "Galle": (6.0360, 79.9179),
            "Jaffna": (9.6606, 80.0140),
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
        self.lat, self.lon = self.cities["Colombo"]
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

        # ✅ Smaller Search / Plot button
        self.search_btn = QPushButton("Search / Plot")
        self.search_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 6px 14px;
                border: none;
                border-radius: 8px;
                background-color: #124559;
                color: white;
            }
            QPushButton:hover {
                background-color: #1a6b7b;
            }
            QPushButton:pressed {
                background-color: #0b2f3a;
            }
        """)
        self.search_btn.clicked.connect(self.on_search)
        controls.addWidget(self.search_btn)
        main_layout.addLayout(controls)

        main_content = QHBoxLayout()
        self.canvas = SkyCanvas(self)
        main_content.addWidget(self.canvas, stretch=3)

        self.info_label = QLabel("Planet details will appear here")
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignTop)
        self.info_label.setMinimumWidth(300)
        main_content.addWidget(self.info_label, stretch=1)
        main_layout.addLayout(main_content)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.apply_theme()

    # -------- OTHER FUNCTIONS --------
    def update_coordinates(self, city_name):
        self.lat, self.lon = self.cities.get(city_name, (0.0, 0.0))

    def on_search(self):
        try:
            text_color = self._text_color
            highlight_color = self._highlight_color
            lat, lon = self.lat, self.lon
            qdt = self.dt_edit.dateTime().toUTC()
            dt = datetime(qdt.date().year(), qdt.date().month(), qdt.date().day(),
                          qdt.time().hour(), qdt.time().minute(), qdt.time().second(),
                          tzinfo=timezone.utc)
            sel_body = self.body_cb.currentText()
            bodies = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
            data, hidden_reasons = [], []

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
                image_html = f"<div style='text-align:center; margin-bottom:15px;'><img src='{image_path}' width='150' height='150'></div>"
            else:
                image_html = f"<p style='color:{highlight_color}; text-align:center;'>Image not available</p>"

            details_html = f"""
            <h1 style='color:{highlight_color}; text-align:center;'>{sel_body}</h1>
            <p><b>UTC:</b> {dt.isoformat()}</p>
            <table style='border-spacing:6px; color:{text_color};'>
                <tr><td><b>Azimuth:</b></td><td>{chosen['az_deg']:.2f}°</td></tr>
                <tr><td><b>Altitude:</b></td><td>{chosen['alt_deg']:.2f}°</td></tr>
                <tr><td><b>Right Ascension:</b></td><td>{chosen['ra_hours']:.4f} h</td></tr>
                <tr><td><b>Declination:</b></td><td>{chosen['dec_deg']:.4f}°</td></tr>
                <tr><td><b>Distance:</b></td><td>{chosen['distance_au']:.4f} AU</td></tr>
            </table>
            """

            hidden_html = ""
            if hidden_reasons:
                hidden_html += f"<h2 style='color:{highlight_color};'>Hidden Bodies</h2><ul style='color:{text_color};'>"
                for reason in hidden_reasons:
                    hidden_html += f"<li>{reason}</li>"
                hidden_html += "</ul>"

            info = f"<div style='color:{text_color};'>{image_html}{details_html}{hidden_html}</div>"
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
    win.showMaximized()
    sys.exit(app.exec_())
