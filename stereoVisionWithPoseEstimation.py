import sys
import cv2
import numpy as np
import time
import imutils
from matplotlib import pyplot as plt

# Function for stereo vision and depth estimation
import triangulation as tri
import calibration

# Mediapipe for face detection
import mediapipe as mp
import time

mp_posedetector = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

# Open both cameras
cap_right = cv2.VideoCapture(1, cv2.CAP_DSHOW)                    
cap_left =  cv2.VideoCapture(0, cv2.CAP_DSHOW)


# Stereo vision setup parameters
frame_rate = 120    #Camera frame rate (maximum at 120 fps)
B = 25               #Distance between the cameras [cm]
f = 8              #Camera lense's focal length [mm]
alpha = 56.6        #Camera field of view in the horisontal plane [degrees]




# Main program loop with face detector and depth estimation using stereo vision
with mp_posedetector.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_detection:

    while(cap_right.isOpened() and cap_left.isOpened()):

        succes_right, frame_right = cap_right.read()
        succes_left, frame_left = cap_left.read()

    ################## CALIBRATION #########################################################

        frame_right, frame_left = calibration.undistortRectify(frame_right, frame_left)

    ########################################################################################

        # If cannot catch any frame, break
        if not succes_right or not succes_left:                    
            break

        else:

            start = time.time()
            
            # Convert the BGR image to RGB
            frame_right = cv2.cvtColor(frame_right, cv2.COLOR_BGR2RGB)
            frame_left = cv2.cvtColor(frame_left, cv2.COLOR_BGR2RGB)

            # Process the image and find faces
            results_right = pose_detection.process(frame_right)
            results_left = pose_detection.process(frame_left)

            # Convert the RGB image to BGR
            frame_right = cv2.cvtColor(frame_right, cv2.COLOR_RGB2BGR)
            frame_left = cv2.cvtColor(frame_left, cv2.COLOR_RGB2BGR)


            ################## CALCULATING DEPTH #########################################################

            center_right = 0
            center_left = 0

            if results_right.pose_landmarks:
                
                mp_draw.draw_landmarks(frame_right, results_right.pose_landmarks, mp_posedetector.POSE_CONNECTIONS)
                landmark = list(results_right.pose_landmarks.landmark)
                #print(landmark[0].x)
                #print(landmark[0].y)
                #bBox = results_right.pose_landmarks.location_data.relative_bounding_box

                h, w, c = frame_right.shape

                #boundBox = int(landmark[0].x * w), int(landmark[0].y * h)

                #center_point_right = (boundBox[0] + boundBox[2] / 2, boundBox[1] + boundBox[3] / 2)
                center_point_right = (landmark[0].x * w, landmark[0].y * h)

                #cv2.putText(frame_right, f'{int(detection.score[0]*100)}%', (boundBox[0], boundBox[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 2)


            if results_left.pose_landmarks:
                mp_draw.draw_landmarks(frame_left, results_left.pose_landmarks, mp_posedetector.POSE_CONNECTIONS)
                landmark = list(results_left.pose_landmarks.landmark)

                #bBox = detection.location_data.relative_bounding_box

                h, w, c = frame_left.shape

                #boundBox = int(bBox.xmin * w), int(bBox.ymin * h), int(bBox.width * w), int(bBox.height * h)

                center_point_left = (landmark[0].x * w, landmark[0].y * h)

                #cv2.putText(frame_left, f'{int(detection.score[0]*100)}%', (boundBox[0], boundBox[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 2)




            # If no ball can be caught in one camera show text "TRACKING LOST"
            if not results_right.pose_landmarks or not results_left.pose_landmarks:
                cv2.putText(frame_right, "TRACKING LOST", (75,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),2)
                cv2.putText(frame_left, "TRACKING LOST", (75,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),2)

            else:
                # Function to calculate depth of object. Outputs vector of all depths in case of several balls.
                # All formulas used to find depth is in video presentaion
                depth = tri.find_depth(center_point_right, center_point_left, frame_right, frame_left, B, f, alpha)

                cv2.putText(frame_right, "Distance: " + str(round(depth,1)), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0),3)
                cv2.putText(frame_left, "Distance: " + str(round(depth,1)), (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0),3)
                # Multiply computer value with 205.8 to get real-life depth in [cm]. The factor was found manually.
                print("Depth: ", str(round(depth,1)))



            end = time.time()
            totalTime = end - start

            fps = 1 / totalTime
            #print("FPS: ", fps)

            cv2.putText(frame_right, f'FPS: {int(fps)}', (20,450), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 2)
            cv2.putText(frame_left, f'FPS: {int(fps)}', (20,450), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 2)                                   


            # Show the frames
            cv2.imshow("frame right", frame_right) 
            cv2.imshow("frame left", frame_left)


            # Hit "q" to close the window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


# Release and destroy all windows before termination
cap_right.release()
cap_left.release()

cv2.destroyAllWindows()