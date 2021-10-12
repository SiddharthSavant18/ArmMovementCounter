import cv2
import mediapipe as mp 
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

counter = 0 
stage = None

def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle

cap = cv2.VideoCapture(0)
with mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5) as pose:
	while cap.isOpened():
		ret, frame = cap.read()

		image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		image.flags.writeable = False
		results = pose.process(image)

		image.flags.writeable = True
		image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

		try:
			landmarks = results.pose_landmarks.landmark

			shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
			elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
			wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

			angle = calculate_angle(shoulder, elbow, wrist)

			cv2.putText(image, str(angle),
				tuple(np.multiply(elbow, [640, 480]).astype(int)),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
			
			if angle > 120:
				stage = "down"
			# if angle < 90:
				# stage = "down"
			# if angle > 90 and angle < 120:
			if angle < 90 and stage == 'down':
				stage = "up"
				counter += 1
				print(counter)
				
		except:
			pass

		cv2.putText(image, 'COUNT ', (15,12),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
		cv2.putText(image, str(counter),
        	(10,60),cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        
       	
		cv2.putText(image, ' STAGE', (75,12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
		cv2.putText(image, stage, 
                    (100,60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)

		mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
			mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
			mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

		cv2.imshow("Mediapipe Angle Detect", image)

		if cv2.waitKey(10) & 0xFF == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()