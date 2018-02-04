#Source: https://github.com/sashagaz/Hand_Detection

# For QHacks 2018 - Sean Remedios, Taylor Simpson, Jacob Klein, Monica Rao

#Send Position, Angle

import cv2
import numpy as np
import time

#open("switch.txt", 'w').close()
open("hand.txt", 'w').close()

#Open Camera object
cap = cv2.VideoCapture(0)

#Decrease frame size
if hasattr(cv2, 'cv'):
	cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1400)
	cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 850)
else:
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1400)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 850)

def nothing(x):
	pass

# Function to find angle between two vectors
def Angle(v1,v2):
	dot = np.dot(v1,v2)
	x_modulus = np.sqrt((v1*v1).sum())
	y_modulus = np.sqrt((v2*v2).sum())
	cos_angle = dot / x_modulus / y_modulus
	angle = np.degrees(np.arccos(cos_angle))
	return angle

# Function to find distance between two points in a list of lists
def FindDistance(A,B): 
	return np.sqrt(np.power((A[0][0]-B[0][0]),2) + np.power((A[0][1]-B[0][1]),2)) 
 

# Creating a window for HSV track bars
cv2.namedWindow('HSV_TrackBar')

# Starting with 100's to prevent error while masking
h,s,v = 100,100,100

# Creating track bar
cv2.createTrackbar('h', 'HSV_TrackBar',0,179,nothing)
cv2.createTrackbar('s', 'HSV_TrackBar',0,255,nothing)
cv2.createTrackbar('v', 'HSV_TrackBar',0,255,nothing)

# To track finger movement - Initialized to -1 so everything is bigger
previousFinger = [(-1,-1), (-1,-1), (-1,-1), (-1,-1), (-1,-1)]
# Gesture size in pixels - for determining swipe
GESTURESIZE = 0
#Max distance in pixels - for determining if hand movement was complete jerk
MAX_DISTANCE = 400

#Make sure we can run this as a thread later
#Messy code since it was adapted from other source
#To difficult to change to nice code in this time so you'll have to deal with this!
def handMovement():
	while(1):

		#Measure execution time 
		start_time = time.time()
		
		#Capture frames from the camera
		ret, frame = cap.read()
		
		#Blur the image
		blur = cv2.blur(frame,(3,3))
		
		#Convert to HSV color space
		hsv = cv2.cvtColor(blur,cv2.COLOR_BGR2HSV)
		
		#Create a binary image with where white will be skin colors and rest is black
		mask2 = cv2.inRange(hsv,np.array([2,50,50]),np.array([15,255,255]))
		
		#Kernel matrices for morphological transformation    
		kernel_square = np.ones((11,11),np.uint8)
		kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
		
		#Perform morphological transformations to filter out the background noise
		#Dilation increase skin color area
		#Erosion increase skin color area
		dilation = cv2.dilate(mask2,kernel_ellipse,iterations = 1)
		erosion = cv2.erode(dilation,kernel_square,iterations = 1)    
		dilation2 = cv2.dilate(erosion,kernel_ellipse,iterations = 1)    
		filtered = cv2.medianBlur(dilation2,5)
		kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(8,8))
		dilation2 = cv2.dilate(filtered,kernel_ellipse,iterations = 1)
		kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
		dilation3 = cv2.dilate(filtered,kernel_ellipse,iterations = 1)
		median = cv2.medianBlur(dilation2,5)
		ret,thresh = cv2.threshold(median,127,255,0)
		
		#im2 not used, needed for function return
		#Find contours of the filtered frame
		im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)   

		#Draw Contours
		#cv2.drawContours(frame, contours, -1, (122,122,0), 3)
		#cv2.imshow('Dilation',median)
		
		#Find Max contour area (Assume that hand is in the frame)
		max_area = 100
		ci = 0	
		for i in range(len(contours)):
			cnt = contours[i]
			area = cv2.contourArea(cnt)
			if(area > max_area):
				max_area = area
				ci = i
		
	#	if ci < len(contours)-1:
	#		continue
		#Largest area contour
		try:
			cnts = contours[ci]
		except:
			print ("Error bitch") 			  
		

		#Find convex hull
		hull = cv2.convexHull(cnts)
		
		#Find convex defects
		hull2 = cv2.convexHull(cnts,returnPoints = False)
		defects = cv2.convexityDefects(cnts,hull2)
		
		#Get defect points and draw them in the original image
		FarDefect = []
		for i in range(defects.shape[0]):
			s,e,f,d = defects[i,0]
			start = tuple(cnts[s][0])
			end = tuple(cnts[e][0])
			far = tuple(cnts[f][0])
			FarDefect.append(far)
			#cv2.line(frame,start,end,[0,255,0],1)
			#cv2.circle(frame,far,10,[100,255,255],3)
		
		#Find moments of the largest contour
		moments = cv2.moments(cnts)
		
		#Central mass of first order moments
		if moments['m00']!=0:
			cx = int(moments['m10']/moments['m00']) # cx = M10/M00
			cy = int(moments['m01']/moments['m00']) # cy = M01/M00
		centerMass = (cx,cy)    
		
		#Draw center mass
		cv2.circle(frame,centerMass,7,[100,0,255],2)
		font = cv2.FONT_HERSHEY_SIMPLEX
		#cv2.putText(frame,'Center',tuple(centerMass),font,2,(255,255,255),2)     
		
		#Distance from each finger defect(finger webbing) to the center mass
		distanceBetweenDefectsToCenter = []
		for i in range(0,len(FarDefect)):
			x =  np.array(FarDefect[i])
			centerMass = np.array(centerMass)
			distance = np.sqrt(np.power(x[0]-centerMass[0],2)+np.power(x[1]-centerMass[1],2))
			distanceBetweenDefectsToCenter.append(distance)
		
		#Get an average of three shortest distances from finger webbing to center mass
		sortedDefectsDistances = sorted(distanceBetweenDefectsToCenter)
		AverageDefectDistance = np.mean(sortedDefectsDistances[0:2])
	 
		#Get fingertip points from contour hull
		#If points are in proximity of 80 pixels, consider as a single point in the group
		finger = []
		for i in range(0,len(hull)-1):
			if (np.absolute(hull[i][0][0] - hull[i+1][0][0]) > 80) or ( np.absolute(hull[i][0][1] - hull[i+1][0][1]) > 80):
				if hull[i][0][1] < 500:
					finger.append(hull[i][0])
		
		#The fingertip points are 5 hull points with largest y coordinates  
		finger =  sorted(finger,key=lambda x: x[1])   
		fingers = finger[0:5]
		
		#Calculate distance of each finger tip to the center mass
		fingerDistance = []
		vList = []
		for i in range(0,len(fingers)):
			distance = np.sqrt(np.power(fingers[i][0]-centerMass[0],2)+np.power(fingers[i][1]-centerMass[0],2))
			fingerDistance.append(distance)
		
			#Only get one point that is the largest distance from the center of mass (longest finger)
			if max(fingerDistance) == distance:
				#Deltas for determining gesture distance
				pointToPlace = (fingers[i][0], fingers[i][1])
				deltaX = previousFinger[i][0] - pointToPlace[0]
				deltaY = previousFinger[i][1] - pointToPlace[1]
				absDeltaX = np.absolute(deltaX)
				absDeltaY = np.absolute(deltaY)
				#Find the fingers and place a circle on them
				#cv2.circle(frame, pointToPlace, 10, [100,255,255], 3)
				cv2.circle(frame, pointToPlace, 10, [0,255,0], 3)

				#Write to file for game use
				fileWrHand = open("hand.txt","a+")
				if fingers[i][0] != 0 and fingers[i][1] != 0:
					fileWrHand.write("%s" % (pointToPlace, ))
				fileWrHand.close

				#Make sure the previous point wasn't a default
				if (previousFinger[i][0] != -1 or previousFinger[i][1] != -1) and (previousFinger[i][0] != 0 or previousFinger[i][1] != 0):
					#Gesture distance is a swipe
					if absDeltaX >= GESTURESIZE or absDeltaY >= GESTURESIZE:
						#Makes sure it wasn't a hand movement or complete jerk
						if absDeltaX > MAX_DISTANCE or absDeltaY > MAX_DISTANCE-100:
							continue
						#cv2.line(frame,previousFinger[i],pointToPlace,[0,255,0],1)
						#Get an angle
						point1 = list(previousFinger[i])
						point2 = list(pointToPlace)
						vList = [point1, point2]
						vector = np.array(vList)
						DEFAULT_VECTOR = np.array([point1,[1000,point2[1]]])
						swipeAngle = Angle(DEFAULT_VECTOR, vector)
						#print ("Previous Finger: %s" % (previousFinger[i],) + " - Moved Finger: %s" % (pointToPlace,) + " - Angle: %s" % swipeAngle)
			previousFinger[i] = pointToPlace #The new point is now a past point

		fileWr = open("switch.txt","a+")
		if len(vList) > 1:
			fileWr.write("%s" % vList)
		fileWr.close

		#Finger is pointed/raised if the distance of between fingertip to the center mass is larger
		#than the distance of average finger webbing to center mass by 130 pixels
		result = 0
		for i in range(0,len(fingers)):
			if fingerDistance[i] > AverageDefectDistance+130:
				result = result + 1
		
		#Print number of pointed fingers
		#cv2.putText(frame,str(result),(100,100),font,2,(255,255,255),2)
			
		#Print bounding rectangle
		x,y,w,h = cv2.boundingRect(cnts)
		#img = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
		
		#cv2.drawContours(frame,[hull],-1,(255,255,255),2)
		
		#Flip the image to mirror
		#frame = cv2.flip(frame, 1)
		##### Show final image ########
		cv2.imshow('Greenland',frame)
		###############################
		
		#Print execution time
		#print time.time()-start_time

		#Calm down there boy
		#time.sleep(10)
		
		#close the output video by pressing 'ESC'
		k = cv2.waitKey(5) & 0xFF
		if k == 27:
			break

handMovement()

cap.release()
cv2.destroyAllWindows()
