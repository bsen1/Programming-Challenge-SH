import requests
import time
from datetime import datetime
from shapely.geometry import Point, Polygon
import threading

from emailer import send_alert

BASE_URL = "https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test/clinicianstatus"
CLINICIAN_IDS = [1,2,3,4,5,6,7]
DELAY_INTERVAL_SECONDS = 5
ALERT_INTERVAL_SECONDS = 120

# Check if Clinician in ANY zone
def is_in_zone(clinician_location, zones):
    point = Point(clinician_location)
    polygons = [Polygon(zone) for zone in zones]
    
    in_zone = False
    for polygon in polygons:
        if polygon.covers(point):
            in_zone = True
            break

    return in_zone

# Main Polling Loop
def start():
    print("STARTING POLL")
    
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

                error_msg = f"[API] {display_time_now} Failed to fetch status for clinician #{cid}: {e}\n"
                with open("errors.txt", "a") as f:
                    f.write(error_msg)
                threading.Thread(target=send_alert, args=(cid, error_msg)).start()
                continue

            features = data.get("features")
            if not features:
                error_msg = f"[ERROR] {display_time_now} Clinician #{cid}: bad response\n"
                with open("errors.txt", "a") as f:
                    f.write(error_msg)
                threading.Thread(target=send_alert, args=(cid, error_msg)).start()
                continue

            clinician_location = features[0]["geometry"]["coordinates"] # [lon, lat]

            if cid == 2:
                zones = features[1]["geometry"]["coordinates"]

            elif cid == 3:
                zones = [features[1]["geometry"]["coordinates"][0], features[2]["geometry"]["coordinates"][0]]

            else:
                zones = [features[1]["geometry"]["coordinates"][0]]


            print(f"CLINICIAN {cid}: ", end="")

            """
            print(f"COORDS: {clinician_location}")
            for i, zone in enumerate(zones):
                print(f"ZONE {i+1}:")
                for point in zone:
                    print(f" {point}")
            """

            in_zone = is_in_zone(clinician_location, zones)
            print("IN ZONE" if in_zone else "NOT IN ZONE")

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
                    with open("alerts.txt", "a") as f:
                        f.write(msg)
                    threading.Thread(target=send_alert, args=(cid, msg)).start()

            else:
                if cid in alert_timestamps:
                    # Has re-entered zone
                    minutes_out = int((time.time() - alert_timestamps[cid]["first"]) / 60)
                    msg = f"[INFO] {display_time_now} Clinician #{cid} has RE-ENTERED their zone after {minutes_out} minute(s)\n"
                    with open("alerts.txt", "a") as f:
                        f.write(msg)
                    threading.Thread(target=send_alert, args=(cid, msg)).start()
                    del alert_timestamps[cid]
        
        print(f"WAITING {DELAY_INTERVAL_SECONDS} SECONDS")
        time.sleep(DELAY_INTERVAL_SECONDS)


if __name__ == "__main__":
    start()