import cv2
import mediapipe as mp
import numpy as np
import pygame
import time
import os

# Initialize Pygame for audio
pygame.mixer.init()

# Load sound files
sounds = {
    'drum': pygame.mixer.Sound('drum.wav'),
    'bass': pygame.mixer.Sound('bass.wav'),
    'guitar': pygame.mixer.Sound('guitar.wav'),
    'chorus': pygame.mixer.Sound('chorus.wav'),
    'cymbal': pygame.mixer.Sound('cymbal.wav')
}

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Gesture detection parameters
gesture_cooldown = 1.0  # seconds between gesture triggers
last_gesture_time = {}
for sound in sounds.keys():
    last_gesture_time[sound] = 0

def detect_gesture(hand_landmarks, hand_type):
    """Detect gestures based on hand landmarks"""
    # Get wrist and fingertip positions
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    
    # Get finger MCP (knuckle) positions
    index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
    
    # Check for open palm (all fingertips higher than MCPs)
    is_open_palm = (index_tip.y < index_mcp.y and 
                   middle_tip.y < middle_mcp.y and 
                   ring_tip.y < ring_mcp.y and 
                   pinky_tip.y < pinky_mcp.y)
    
    # Check for closed fist (all fingertips lower than MCPs)
    is_closed_fist = (index_tip.y > index_mcp.y and 
                     middle_tip.y > middle_mcp.y and 
                     ring_tip.y > ring_mcp.y and 
                     pinky_tip.y > pinky_mcp.y)
    
    # Check for left swipe (hand moving left)
    is_left_swipe = (hand_type == "Left" and wrist.x < 0.3 and thumb_tip.x < wrist.x)
    
    # Check for right swipe (hand moving right)
    is_right_swipe = (hand_type == "Right" and wrist.x > 0.7 and thumb_tip.x > wrist.x)
    
    # Return detected gesture
    if is_open_palm:
        return "open_palm"
    elif is_closed_fist:
        return "closed_fist"
    elif is_left_swipe:
        return "left_swipe"
    elif is_right_swipe:
        return "right_swipe"
    else:
        return None

def play_sound(gesture, hand_type):
    """Play sound based on detected gesture"""
    current_time = time.time()
    
    if gesture == "open_palm" and current_time - last_gesture_time['drum'] > gesture_cooldown:
        sounds['drum'].play()
        last_gesture_time['drum'] = current_time
        return "Playing Drum"
    
    elif gesture == "closed_fist" and current_time - last_gesture_time['bass'] > gesture_cooldown:
        sounds['bass'].play()
        last_gesture_time['bass'] = current_time
        return "Playing Bass"
    
    elif gesture == "left_swipe" and current_time - last_gesture_time['guitar'] > gesture_cooldown:
        sounds['guitar'].play()
        last_gesture_time['guitar'] = current_time
        return "Strumming Guitar"
    
    elif gesture == "right_swipe" and current_time - last_gesture_time['cymbal'] > gesture_cooldown:
        sounds['cymbal'].play()
        last_gesture_time['cymbal'] = current_time
        return "Playing Cymbal"
    
    return None

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    # Variables to track both hands for chorus
    both_hands_raised = False
    left_hand_raised = False
    right_hand_raised = False
    chorus_playing = False
    last_chorus_time = 0
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Error: Failed to capture image from webcam.")
            break
        
        # Flip the image horizontally for a more intuitive mirror view
        image = cv2.flip(image, 1)
        
        # Convert the BGR image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image and detect hands
        results = hands.process(image_rgb)
        
        # Draw hand landmarks on the image
        if results.multi_hand_landmarks:
            left_hand_raised = False
            right_hand_raised = False
            
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Determine if it's left or right hand
                if results.multi_handedness:
                    hand_type = results.multi_handedness[hand_idx].classification[0].label
                    
                    # Detect gesture
                    gesture = detect_gesture(hand_landmarks, hand_type)
                    
                    # Check if hands are raised for chorus
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    if wrist.y < 0.5:  # Hand is raised (top half of screen)
                        if hand_type == "Left":
                            left_hand_raised = True
                        else:
                            right_hand_raised = True
                    
                    # Play sound based on gesture
                    if gesture:
                        sound_played = play_sound(gesture, hand_type)
                        if sound_played:
                            cv2.putText(image, sound_played, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                                        1, (0, 255, 0), 2, cv2.LINE_AA)
            
            # Check if both hands are raised for chorus
            both_hands_raised = left_hand_raised and right_hand_raised
            current_time = time.time()
            
            if both_hands_raised and not chorus_playing and current_time - last_chorus_time > gesture_cooldown:
                sounds['chorus'].play()
                chorus_playing = True
                last_chorus_time = current_time
                cv2.putText(image, "Playing Chorus", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                            1, (0, 255, 0), 2, cv2.LINE_AA)
            elif not both_hands_raised:
                chorus_playing = False
        
        # Display instructions
        cv2.putText(image, "Open Palm: Drum | Closed Fist: Bass", (10, image.shape[0] - 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(image, "Left Swipe: Guitar | Right Swipe: Cymbal", (10, image.shape[0] - 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(image, "Both Hands Raised: Chorus", (10, image.shape[0] - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        
        # Display the resulting frame
        cv2.imshow('AirBand - Gesture Controlled Music', image)
        
        # Exit on 'q' key press
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()