#!/bin/env python3

# Include Libs
import cv2
import numpy as np
# import keyboard
from datetime import datetime


# Flags
record = False
pause = False
deviceID = 0
# 0 = USB webcam
# 1 = MIPI camera
# 2 = IP camera
textOnly = 0




# Global Vars
videoNameTemplate = "uas_footage_"
videoPathTemplate = "./"
SampleText = ["Startup OK"]

putTextTimeoutMax = 15
putTextTimeout = putTextTimeoutMax # Not Actual time scale, try playing with a value to get a better result


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


# Reads the savefile location (Currently useless)
def readRCFile():
    global pause, videoPathTemplate
    print("Reading RC file")
    try:
        # Read first line from config file
        configFile = open(".uasrecrc", "r+")
        videoPathTemplate = configFile.readline()
    except FileNotFoundError as e:
        # Create config file if it doesn't exist
        print("File not found")
        print("Creating file")
        configFile = open(".uasrecrc", "w")
        configFile.writelines([videoPathTemplate])
    print(f"The first line is {videoPathTemplate}")
    configFile.close()


def main():
    global record, SampleText, videoNameTemplate, videoPathTemplate, putTextTimeout, putTextTimeoutMax, pause, deviceID, textOnly
    # capture frames from a camera with device index=0
    # Here we init the capture device (either a MIPI camera or a regular usb web camera)
    print('Entering main')
    print(f'deviceID is {deviceID}')
    try:
        if deviceID == 0:
            cap = cv2.VideoCapture(0)
            #Use below if it's a MIPI camera
        elif deviceID == 1:
            cap = video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
        elif deviceID == 2:
            url = "rtsp://admin:1qaz!QAZ@192.168.1.64"
            cap = cv2.VideoCapture(url)
    except cv2.error as e:
        print(f'Unable to create video capture device: %s', e.error)
        exit()
    print('Done init cam')
    
    # Assemble video path string
    now = datetime.now()
    videoNameString = videoPathTemplate + videoNameTemplate + now.strftime("%m_%d_%Y_%H%M%S") + ".mp4"
    print(f"Path name is {videoNameString}")







    #print("NOW wait for camera opening")


    #while not cap.isOpened():
    #    continue
    # loop runs if capturing has been initialized


    averageR, averageG, averageB = 0,0,0
    if deviceID==1:
        print(gstreamer_pipeline(flip_method=0))

    # Initialize frame dimension and recording file writer
    width= int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height= int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer= cv2.VideoWriter("Dummy.mp4", cv2.VideoWriter_fourcc(*'DIVX'), 20, (width,height))
    


    cv2.namedWindow('UAS Recorder')
    # Use dummy frame if text only is enabled
    dummy = np.zeros((height, width, 3), dtype = "uint8")

    while(1): 

        # reads frame from a camera 
        ret, frame = cap.read()
        try:
            averageB, averageG, averageR = frame.mean(axis=0).mean(axis=0)
        except AttributeError:
            continue
        if not(pause) and record:
            # print("writing")
            writer.write(frame)
       

        # Resize the frame if it's oversized
        if width > 1920:
            new_h = height / 2
            new_w = width / 2
            temp = frame.resize(frame, (new_w, new_h))
            frame = temp






        # Write info and stuff
        if putTextTimeout>0:
            putTextTimeout=putTextTimeout-1
        else:
            SampleText = []
        for line in range(len(SampleText)):
            if textOnly == 0:
                cv2.putText(frame, 
                    SampleText[line], 
                    (0, 20+30*line), 
                    cv2.FONT_HERSHEY_SIMPLEX , 1, 
                    (255-averageR, 255-averageG, 255-averageB), 
                    2, 
                    cv2.LINE_4)
            else:
                cv2.putText(dummy,
                    SampleText[line],
                    (0, 20+30*line),
                    cv2.FONT_HERSHEY_SIMPLEX , 1,
                    (255, 255, 255),
                    2,
                    cv2.LINE_4)

        # Quick fix overlapping text in text-Only mode
        if putTextTimeout==0:
            dummy = np.zeros((height, width, 3), dtype = "uint8")
        
        # Display the frame
        if textOnly == 0:
            cv2.imshow('UAS Recorder',frame) 
        else:
            frame = dummy
            cv2.imshow('UAS Recorder', frame)

        # Wait for 25ms
        # need to deal with textOnly mode
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('r'):
            putTextTimeout = putTextTimeoutMax
            # print("R pressed")
            if not record:
                record = True
                videoNameString = videoPathTemplate + videoNameTemplate + now.strftime("%m_%d_%Y_%H%M%S") + ".mp4"
                writer= cv2.VideoWriter(videoNameString, cv2.VideoWriter_fourcc(*'DIVX'), 20, (width,height))
            else:
                pause = not(pause)
            # print(f"Record is now {pause}")
            recordString = "N/A"
            if not(record) and not(pause):
                recordString = ""
            elif record and not(pause):
                recordString = "REC"
            elif record and pause:
                recordString = "PAUSED"
            SampleText = [recordString]
            # if pause:
            #     print("PAUSED")
        elif key == ord('h'):
            putTextTimeout = putTextTimeoutMax
            SampleText = ["[r] to start or pause recording", "[s] to stop and save recording", "[t] for status", "[+] or [-] to change delay", "[p] to turn on/off live preview", "[h] to quit"]
        elif key == ord('t'):
            putTextTimeout = putTextTimeoutMax*2
            isRecordString = "YES" if record and not(pause) else "NO"
            isPauseString = "N/A"
            if record and not(pause):
                isPauseString = "NO"
            elif record and pause:
                isPauseString = "YES"
            elif not (record) and not (pause):
                isPauseString = "STOPPED REC"
                SampleText = [f"Recording? = {isRecordString}", 
                        f"Paused? = {isPauseString}", f"FileName? = {videoNameString}",
                         f"Delay? = {putTextTimeoutMax}", f"DIMENSION? = {width}X{height}"]
        elif key == ord('s'):
            putTextTimeout = putTextTimeoutMax*2
            writer.release()        
            SampleText = [f"Saved to {videoNameString}", f"at {videoPathTemplate}"]
            record = False
            pause = False
        elif key == ord('=') or key == ord('+'):
            putTextTimeout = putTextTimeoutMax
            if putTextTimeoutMax<100:
                putTextTimeoutMax = putTextTimeoutMax+5
                if putTextTimeoutMax==100:
                    SampleText = [f"Delay increased to {putTextTimeoutMax} (MAX)"]
                else:
                    SampleText = [f"Delay increased to {putTextTimeoutMax}"]
        elif key == ord('-'):
            putTextTimeout = putTextTimeoutMax
            if putTextTimeoutMax>0:
                putTextTimeoutMax = putTextTimeoutMax-5
                if putTextTimeoutMax==0:
                    SampleText = [f"Delay increased to {putTextTimeoutMax} (MIN)"]
                else:
                    SampleText = [f"Delay increased to {putTextTimeoutMax}"]
        elif key == ord('p'):
            putTextTimeout = putTextTimeoutMax
            textOnly = 1 - textOnly
            previewModeString = "ON" if textOnly == 1 else "OFF"
            SampleText = [f"No Preview Mode is {previewModeString}"]
    # Clean up
    cap.release()
    writer.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    readRCFile()
    main()
