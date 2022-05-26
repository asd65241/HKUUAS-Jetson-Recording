#!/bin/env python3
import pandas as pd
import cv2

# gstremer pipeline function
def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=960,
    display_height=540,
    framerate=60,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d !"
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )



camTypes = ["0: USB webcam", "1: MIPI (CSI) camera", "2: RTSP camera"]
#url = "https://en.wikipedia.org/wiki/List_of_common_resolutions"
url = "./res.html"
table = pd.read_html(url)[0]
table.columns = table.columns.droplevel()

resolutions = {}
print("Welcome to camera resolution selection program!")
print("Please select your camera:")
for line in camTypes:
    print(line)
while True:
    choice = input()
    if int(choice) in range(0,3):
        break
    else:
        print("Invalid Choice")

print(f"You have selected {camTypes[int(choice)]}")
if choice == '0':
    cap = cv2.VideoCapture(0)
elif choice == '1':
    cap = video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)  
elif choice == '2':
    url = "rtsp://admin:1qaz!QAZ@192.168.1.64"
    cap = cv2.VideoCapture(url)               
for index, row in table[["W", "H"]].iterrows():
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, row["W"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, row["H"])
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    resolutions[str(width)+"x"+str(height)] = "OK"
print("The available resolutions are:")
for line in resolutions:
    print(line)

