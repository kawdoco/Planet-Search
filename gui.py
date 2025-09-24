# gui.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QDateTimeEdit, QMessageBox
)
from PyQt5.QtCore import QDateTime, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime, timezone
import numpy as np
from solarsystem import PlanetEngine



from planet import Planet

class SkyCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5,5))
        super().__init__(fig)
        self.ax = fig.add_subplot(111, polar=True)
        self.ax.set_theta_zero_location("N")  # 0 at North
        self.ax.set_theta_direction(-1)  # clockwise
        self.ax.set_rlim(90, 0)  # show altitude as radius inverted (90 top, 0 bottom)

    def plot_bodies(self, data_list):
        self.ax.clear()
        self.ax.set_theta_zero_location("N")
        self.ax.set_theta_direction(-1)
        self.ax.set_rlim(90, 0)
        for item in data_list:
            az = np.deg2rad(item['az_deg'])
            alt = item['alt_deg']
            label = item['name']
            self.ax.scatter(az, 90-alt, s=50)  # convert alt->radius
            self.ax.text(az, 90-alt, " " + label)
        self.ax.set_title("Sky view (azimuth=N=0°, radius = 90°-altitude)")
        self.draw()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Planet/Star Search Simulation")
        self.setGeometry(100,100,800,600)
        layout = QVBoxLayout()

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Observer Lat:"))
        self.lat_cb = QComboBox()
        # quick presets
        self.lat_cb.addItem("0.0", 0.0)
        self.lat_cb.addItem("6.9271 (Colombo)", 6.9271)
        self.lat_cb.addItem("51.5074 (London)", 51.5074)
        controls.addWidget(self.lat_cb)

        controls.addWidget(QLabel("Lon:"))
        self.lon_cb = QComboBox()
        self.lon_cb.addItem("0.0", 0.0)
        self.lon_cb.addItem("79.8612 (Colombo)", 79.8612)
        self.lon_cb.addItem("-0.1278 (London)", -0.1278)
        controls.addWidget(self.lon_cb)

        controls.addWidget(QLabel("Body:"))
        self.body_cb = QComboBox()
        bodies = ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"]
        for b in bodies:
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

        # Canvas
        self.canvas = SkyCanvas(self)
        layout.addWidget(self.canvas)

        # engine
        # inside MainWindow.__init__
        self.engine = PlanetEngine()

        self.setLayout(layout)

    def on_search(self):
        lat = float(self.lat_cb.currentData())
        lon = float(self.lon_cb.currentData())
        # convert QDateTime to python datetime (UTC)
        qdt = self.dt_edit.dateTime().toUTC()
        dt = datetime(
            qdt.date().year(), qdt.date().month(), qdt.date().day(),
            qdt.time().hour(), qdt.time().minute(), qdt.time().second(),
            tzinfo=timezone.utc
        )
        sel_body = self.body_cb.currentText()
        try:
            # we'll compute all bodies and highlight selected too (makes UI exploration easier)
            bodies = ["Mercury","Venus","Mercury","Mars","Jupiter","Saturn","Uranus","Neptune"]
            data = []
            for b in bodies:
                pos = self.engine.body_position(b, observer_latlon=(lat,lon), when=dt)
                pos['name'] = b
                data.append(pos)
            self.canvas.plot_bodies(data)
            # show a popup with the chosen body's details
            chosen = next(item for item in data if item['name']==sel_body)
            info = (f"{sel_body} @ {dt.isoformat()} UTC\n"
                    f"Azimuth: {chosen['az_deg']:.2f}°\n"
                    f"Altitude: {chosen['alt_deg']:.2f}°\n"
                    f"RA: {chosen['ra_hours']:.4f} h\n"
                    f"Dec: {chosen['dec_deg']:.4f}°\n"
                    f"Distance (AU): {chosen['distance_au']:.4f}")
            QMessageBox.information(self, f"{sel_body} position", info)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
