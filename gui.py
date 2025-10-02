import sys
from PyQt5.QtWidgets import QTextEdit

from PyQt5.QtWidgets import QLabel, QFrame
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


class SkyCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(5,5))
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
            self.ax.scatter(az, 90-alt, s=50)  
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
        bodies = ["Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune"]
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
#-------------------------------
      
        main_content = QHBoxLayout()

        self.canvas = SkyCanvas(self)
        main_content.addWidget(self.canvas, stretch=3)

        self.info_label = QLabel("Planet details will appear here")
        self.info_label.setWordWrap(True)
        self.info_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.info_label.setMinimumWidth(250)
        main_content.addWidget(self.info_label, stretch=1)

        layout.addLayout(main_content)

        
        self.engine = PlanetEngine()

        self.setLayout(layout)

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
            info = (f"<h3>{sel_body}</h3>"
                    f"UTC: {dt.isoformat()}<br>"
                    f"Azimuth: {chosen['az_deg']:.2f}°<br>"
                    f"Altitude: {chosen['alt_deg']:.2f}°<br>"
                    f"RA: {chosen['ra_hours']:.4f} h<br>"
                    f"Dec: {chosen['dec_deg']:.4f}°<br>"
                    f"Distance (AU): {chosen['distance_au']:.4f}")

            if chosen['alt_deg'] <= 0:
                info += "<br><span style='color:red'>⚠️ Not visible (below horizon)</span>"

            if hidden_reasons:
                info += "<br><br><b>Other hidden bodies:</b><br>" + "<br>".join(hidden_reasons)

            
            self.info_label.setText(info)

        except Exception as e:
            self.info_label.setText(f"<span style='color:red'>Error: {str(e)}</span>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())