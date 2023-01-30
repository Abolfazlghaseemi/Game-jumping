import cv2
import os
 
# storing the path of modules file
# in variable file_path
file_path = cv2.__file__
 
# storing the directory in dir variable
dir = os.path.dirname(file_path)
 
# printing the directory
print(dir)