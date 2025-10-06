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

      # --- Main content: Canvas + Info Panel side by side ---
        main_content = QHBoxLayout()

        # Canvas
        self.canvas = SkyCanvas(self)
        main_content.addWidget(self.canvas, stretch=3)

        # Info panel
        self.info_label = QLabel("Planet details will appear here")
        self.info_label.setWordWrap(True)
        self.info_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.info_label.setMinimumWidth(250)


        # --- Set dark blue background for the info panel ---
        self.info_label.setStyleSheet("""
            background-color: #01161e;
            color: white;
            border: 1px solid #124559;
            border-radius: 6px;
            padding: 10px;
        """)

        
        main_content.addWidget(self.info_label, stretch=1)

        layout.addLayout(main_content)

        # engine
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
            info = f"""
            <div style="font-family: Times New Roman; font-size: 12pt; color: #222;background-color: #e0f7fa; padding:10px; border-radius:6px;">
                <h1 style="color:#a14a10; margin-bottom:4px;">{sel_body}</h1>
                <p><b>UTC:    </b> {dt.isoformat()}</p>
                <table style="border-spacing: 6px;">
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
                    \n\n⚠️ Not visible on sky map because it is below the horizon.
                    
                </p>
                """
    

            if hidden_reasons:
                info += "<h2 style='margin-top:10px; color:#f5e342;'><br>Other Hidden Bodies</h2><ul>"
                for reason in hidden_reasons:
                    info += f"<li>{reason}</li>"
                info += "</ul>"

            info += "</div>"


            # --- Show in side panel only ---
            self.info_label.setText(info)

        except Exception as e:
            self.info_label.setText(f"<span style='color:red'>Error: {str(e)}</span>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())