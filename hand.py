import cv2
import mediapipe as mp
from random import random
from numpy import sqrt,ceil
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
import time


randX, randY = 0.8*random(), 0.8*random()
counting = 0
isPlaying = False
timer = 0
highlight = False
getReady = False

#settings
radius = 15
circleRadius = 50
drawHands = False
timerTime = 5
highlightTime = 3
getReadyTime = 3

#TEXT settings
menuOrg = (75,50)
menuFontScale = 1
menuRGB = (100,100,255)
getReadyOrg = (150,250)
getReadyTextOrg = (50,400)
getReadyFontScale = 10
getReadyTextFontScale = 3
getReadyRGB = (255,0,255)
getReadyGoRGB = (0,0,255)
highlightOrg = (100,250)
highlightFontScale = 3
org = (150, 50)
fontScale = 1
color = (255, 0, 0)
thickness = 2
font = cv2.FONT_HERSHEY_SIMPLEX

#MENU settings
menuCircleRadius = 75 
menuCircleY = 200
menuCircle1X = 100
menuCircle2X = 640 - menuCircle1X
menuCircleThickness = 3
menuCircleRGB = (243,122,72)
# For webcam input:

cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    max_num_hands = 2,
    ) as hands:
  while cap.isOpened():
    
    success, image = cap.read()
    image = cv2.flip(image,1)
    image_height,image_width = image.shape[:2]
    isInside = False
    circleX = int(randX*image_width)
    circleY = int(randY*image_height)
    frameTime = time.time()

    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue
    
    # False equals better performance, low quality 
    image.flags.writeable = False

    # On non-linux 
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks and not highlight:
      landmarks = results.multi_hand_landmarks
      isPlaying = True
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())

        for landmark in hand_landmarks.landmark:
          x = int(landmark.x * image_width)
          y = int(landmark.y * image_height)
          

          if drawHands: 
            cv2.circle(image,(x,y),radius=radius,color=(0,0,255))

          distance = sqrt((x - circleX)**2 + (y - circleY)**2)
          if distance <= radius + circleRadius and not isInside:
            counting+=1
            isInside = True
          
          if isPlaying and timer==0:
            distance1 = sqrt((x - menuCircle1X)**2 + (y-menuCircleY)**2)
            distance2 = sqrt((x - menuCircle2X)**2 + (y-menuCircleY)**2)

            if not (distance1 <= radius+menuCircleRadius or distance2 <= radius+menuCircleRadius):
              isPlaying = False
    
    if isPlaying:
      if getReady:
        timeLeft = getReadyTimer - frameTime
        if timeLeft < 0:
          cv2.putText(image,'GO!',getReadyTextOrg,font,getReadyFontScale,getReadyGoRGB,thickness,cv2.LINE_AA,False)
          getReady = False
          timer = frameTime + timerTime
        else:
          cv2.putText(image,str(int(ceil(timeLeft))),getReadyOrg,font,getReadyFontScale,getReadyRGB,thickness,cv2.LINE_AA,False)
          cv2.putText(image,'GET READY!',getReadyTextOrg,font,getReadyTextFontScale,getReadyRGB,thickness,cv2.LINE_AA,False)
      elif timer == 0:
        getReady = True
        getReadyTimer = frameTime + getReadyTime
        timer = frameTime + timerTime
      elif timer < frameTime:
        timer = 0
        print(f'END OF GAME, SCORE: {counting}')
        isPlaying = False
        highlight = True
        highlightTimer = frameTime + highlightTime
      elif not getReady:
        cv2.circle(image,(circleX,circleY),radius=circleRadius, color=(0,255,0),thickness=thickness)
        cv2.putText(image,str(counting),org,font,fontScale,color,thickness,cv2.LINE_AA,False)

    elif highlight:
      text = f'Game over! Score: {counting}'
      cv2.putText(image,text,highlightOrg,font,fontScale,color,thickness,cv2.LINE_AA,False)
      if highlightTimer < frameTime:
        counting = 0
        highlight = False

    # Menu
    elif not (isPlaying and highlight):
      cv2.putText(image,f'Put hands in circles to start!',menuOrg,font,menuFontScale,menuRGB,thickness,cv2.LINE_AA,False)
      cv2.circle(image,(menuCircle1X,menuCircleY),radius=menuCircleRadius, color=menuCircleRGB,thickness=menuCircleThickness)
      cv2.circle(image,(menuCircle2X,menuCircleY),radius=menuCircleRadius, color=menuCircleRGB,thickness=menuCircleThickness)

    if isInside:
      randX, randY = random(), random()

    cv2.imshow('Catch a bubble!', image)
    # ESC to exit
    if cv2.waitKey(5) & 0xFF == 27:
      break
      


cap.release()
