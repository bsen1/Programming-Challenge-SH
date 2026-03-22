import os
from dotenv import load_dotenv
import requests
import time
from datetime import datetime
from shapely.geometry import Point, Polygon

import threading

from emailer import send_alert

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
CLINICIAN_IDS = [1,2,3,4,5,6]
DELAY_INTERVAL_SECONDS = 30 # Time between Polling Rounds
ALERT_INTERVAL_SECONDS = 120 # Time between re-alerts on same clinician

# Check if Clinician in ANY zone
def is_in_zone(clinician_location, zones):
    point = Point(clinician_location)
    polygons = [Polygon(zone) for zone in zones]
    
    in_zone = False
    for polygon in polygons:
        if polygon.covers(point): # covers() includes boundary as in zone
            in_zone = True
            break

    return in_zone

# Main Polling Loop
def start():
    print("Starting clinician monitoring")
    
    # { cid: { "first": timestamp, "last": timestamp } }
    alert_timestamps = {}

    while True:
        for cid in CLINICIAN_IDS:
            url = f"{BASE_URL}/{cid}"
            display_time_now = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

            try:
                response = requests.get(url, timeout=5)
                data = response.json()
            except Exception as e:
                # Alert and skip clinician if API call fails
                error_msg = f"[API] {display_time_now} Failed to fetch status for clinician #{cid} : {e}\n"
                with open("errors.txt", "a") as f:
                    f.write(error_msg)
                threading.Thread(target=send_alert, args=(cid, error_msg)).start()
                continue

            features = data.get("features")
            if not features:
                # Alert and skip clinician if bad response
                error_msg = f"[ERROR] {display_time_now} Clinician #{cid}: bad response\n"
                with open("errors.txt", "a") as f:
                    f.write(error_msg)
                threading.Thread(target=send_alert, args=(cid, error_msg)).start()
                continue

            clinician_location = features[0]["geometry"]["coordinates"] # [lon, lat]


            # Clinicians 2 and 3 have irregular zones
            if cid == 2:
                zones = features[1]["geometry"]["coordinates"]

            elif cid == 3:
                zones = [features[1]["geometry"]["coordinates"][0], features[2]["geometry"]["coordinates"][0]]

            else:
                zones = [features[1]["geometry"]["coordinates"][0]]

            in_zone = is_in_zone(clinician_location, zones)
            if not in_zone:
                print(f"Clinician #{cid} is NOT in zone")

            if not in_zone:

                now = time.time()

                if cid not in alert_timestamps:
                    # First time out
                    alert_timestamps[cid] = {"first" : now, "last" : now}
                    msg = f"[ALERT] {display_time_now} Clinician #{cid} has LEFT their zone\n"

                elif now - alert_timestamps[cid]["last"] >= ALERT_INTERVAL_SECONDS:
                    # Still Out of Zone after Interval
                    minutes_out = int((now - alert_timestamps[cid]["first"]) / 60)
                    alert_timestamps[cid]["last"] = now
                    msg = f"[ALERT] {display_time_now} Clinician #{cid} has been outside their zone for {minutes_out} minute(s)\n"

                else:
                    # Still out of zone but not been long enough to re-alert
                    msg = None

                if msg:
                    # Send email in background thread so it doesn't block the polling loop
                    threading.Thread(target=send_alert, args=(cid, msg)).start()

            else:
                if cid in alert_timestamps:
                    # Has re-entered zone
                    minutes_out = int((time.time() - alert_timestamps[cid]["first"]) / 60)
                    msg = f"[INFO] {display_time_now} Clinician #{cid} has RE-ENTERED their zone after {minutes_out} minute(s)\n"
                    threading.Thread(target=send_alert, args=(cid, msg)).start()
                    del alert_timestamps[cid]
        
        time.sleep(DELAY_INTERVAL_SECONDS)


if __name__ == "__main__":
    start()