import cv2
import mediapipe as mp
import socket
import time

#setting ip, port
ESP32_IP = "IP"
ESP32_PORT = PORT

#initializing
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

#video capture start
cap = cv2.VideoCapture(0)

#define socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = hands.process(image)

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                #get coordinates    
                MCP = [
                    hand_landmarks.landmark[5],
                    hand_landmarks.landmark[9],
                    hand_landmarks.landmark[13],
                    hand_landmarks.landmark[17]
                ]
                wrist = hand_landmarks.landmark[0]
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]
                middle_tip = hand_landmarks.landmark[12]
                ring_tip = hand_landmarks.landmark[16]

                #cac distance
                distance = [0, 0, 0, 0]
                distance[0] = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)**0.5
                distance[1] = ((thumb_tip.x - middle_tip.x)**2 + (thumb_tip.y - middle_tip.y)**2)**0.5
                distance[2] = ((thumb_tip.x - ring_tip.x)**2 + (thumb_tip.y - ring_tip.y)**2)**0.5
                for i in range(0, 4):
                    distance[3] += ((wrist.x - MCP[i].x)**2 + (wrist.y - MCP[i].y)**2)**0.5
                    if i == 3:
                        distance[3] = distance[3]/4

                #z-axis distance correction
                distance_rate = distance[3]/(2/10)
                if distance_rate < 1:
                    distance[0] = distance[0]/(distance_rate*(9/10))
                    distance[1] = distance[1]/distance_rate
                    distance[2] = distance[2]/(distance_rate*(8/10))

                print(distance)

                #transfer distance into RGB
                rgb = [0, 0, 0]
                for i in range(0, 3):
                    rgb[i] = max(0, min(int(distance[i] * (1000 - i*150)), 255))
                    if rgb[i] < 50 * (3-i):
                        rgb[i] = max(0, min(int(distance[i] * (500 - i*150)), 255))
                

                #fire
                sock.sendto(f"{rgb}".encode(), (ESP32_IP, ESP32_PORT))
                print(f"RGB: {(rgb)}")

                #landmark
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        #video output
        cv2.imshow('MediaPipe Hands', image)

        #esc
        if cv2.waitKey(5) & 0xFF == 27:
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    sock.close()
