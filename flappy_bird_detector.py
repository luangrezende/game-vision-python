import cv2
import numpy as np
import mss
import time
import re

def capture_screen_region(monitor):
    with mss.mss() as sct:
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

def detect_bird(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lower_blue = np.array([95, 150, 100])
    upper_blue = np.array([125, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    lower_yellow = np.array([95, 160, 200])
    upper_yellow = np.array([105, 185, 255])
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    lower_red = np.array([5, 200, 200])
    upper_red = np.array([15, 255, 255])
    red_mask = cv2.inRange(hsv, lower_red, upper_red)
    
    lower_cyan = np.array([15, 100, 200])
    upper_cyan = np.array([25, 130, 255])
    cyan_mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
    
    bird_mask = cv2.bitwise_or(blue_mask, yellow_mask)
    bird_mask = cv2.bitwise_or(bird_mask, red_mask)
    bird_mask = cv2.bitwise_or(bird_mask, cyan_mask)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    bird_mask = cv2.morphologyEx(bird_mask, cv2.MORPH_CLOSE, kernel)
    bird_mask = cv2.morphologyEx(bird_mask, cv2.MORPH_OPEN, kernel)
    
    contours, _ = cv2.findContours(bird_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    bird_boxes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100 and area < 2000:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = max(h, w) / min(h, w) if min(h, w) > 0 else 0
            if aspect_ratio < 2.5 and w > 12 and h > 12:
                bird_boxes.append((x, y, w, h))
    
    return bird_boxes

def detect_pipes(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lower_green = np.array([36, 85, 84])
    upper_green = np.array([75, 187, 253])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    bg_lower = np.array([60, 29, 200])
    bg_upper = np.array([80, 157, 252])
    bg_mask = cv2.inRange(hsv, bg_lower, bg_upper)
    
    mask = cv2.bitwise_and(mask, cv2.bitwise_not(bg_mask))
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    kernel_large = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 15))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_large)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    pipe_boxes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        
        if area > 50:
            aspect_ratio = h / w if w > 0 else 0
            if aspect_ratio > 0.3 and w > 5 and h > 8:
                pipe_boxes.append((x, y, w, h))
    
    return pipe_boxes

def detect_gameover(frame):
    return detect_gameover_color_enhanced(frame)

def detect_gameover_color_enhanced(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    frame_height, frame_width = frame.shape[:2]
    
    lower_orange = np.array([10, 100, 100])
    upper_orange = np.array([25, 255, 255])
    orange_mask = cv2.inRange(hsv, lower_orange, upper_orange)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    orange_mask = cv2.morphologyEx(orange_mask, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    gameover_candidates = []
    large_text_found = False
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 30:
            x, y, w, h = cv2.boundingRect(contour)
            
            center_x = x + w/2
            center_y = y + h/2
            
            in_center_x = 0.15 * frame_width < center_x < 0.85 * frame_width
            in_center_y = 0.2 * frame_height < center_y < 0.8 * frame_height
            
            is_large_game_over = (area > 3000 and w > 70 and h > 70 and 
                                 200 < x < 400 and 250 < y < 400)
            
            is_medium_text = (area > 500 and w > 20 and h > 15 and
                             150 < x < 450 and 200 < y < 500)
            
            is_small_text = (area > 50 and area < 500 and w > 10 and h > 8 and
                           in_center_x and in_center_y)
            
            if is_large_game_over:
                large_text_found = True
                gameover_candidates.append((x, y, w, h, area, "LARGE"))
            elif is_medium_text:
                gameover_candidates.append((x, y, w, h, area, "MEDIUM"))
            elif is_small_text:
                gameover_candidates.append((x, y, w, h, area, "SMALL"))
    
    if large_text_found:
        return [(box[0], box[1], box[2], box[3]) for box in gameover_candidates if box[5] == "LARGE"]
    elif len(gameover_candidates) >= 8:
        if gameover_candidates:
            min_x = min(box[0] for box in gameover_candidates)
            min_y = min(box[1] for box in gameover_candidates)
            max_x = max(box[0] + box[2] for box in gameover_candidates)
            max_y = max(box[1] + box[3] for box in gameover_candidates)
            return [(min_x, min_y, max_x - min_x, max_y - min_y)]
    
    return []

def detect_score_text(frame):
    score_region = frame[5:35, 10:150]
    
    hsv = cv2.cvtColor(score_region, cv2.COLOR_BGR2HSV)
    
    lower_white = np.array([0, 0, 220])
    upper_white = np.array([180, 25, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    score_boxes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 20:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 5 and h > 8:
                score_boxes.append((x, y, w, h))
    
    return score_boxes, score_region

def extract_score_from_region(frame):
    score_boxes, score_region = detect_score_text(frame)
    
    if not score_boxes:
        return -1
    
    gray = cv2.cvtColor(score_region, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    resized = cv2.resize(thresh, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    
    contours, _ = cv2.findContours(resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    valid_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        if area > 50 and w > 8 and h > 15:
            valid_contours.append((x, y, w, h))
    
    if not valid_contours:
        return -1
    
    valid_contours.sort(key=lambda c: c[0])
    
    digit_patterns = {
        '0': [
            [1,1,1],
            [1,0,1],
            [1,0,1],
            [1,0,1],
            [1,1,1]
        ],
        '1': [
            [0,1,0],
            [1,1,0],
            [0,1,0],
            [0,1,0],
            [1,1,1]
        ],
        '2': [
            [1,1,1],
            [0,0,1],
            [1,1,1],
            [1,0,0],
            [1,1,1]
        ],
        '3': [
            [1,1,1],
            [0,0,1],
            [1,1,1],
            [0,0,1],
            [1,1,1]
        ],
        '4': [
            [1,0,1],
            [1,0,1],
            [1,1,1],
            [0,0,1],
            [0,0,1]
        ],
        '5': [
            [1,1,1],
            [1,0,0],
            [1,1,1],
            [0,0,1],
            [1,1,1]
        ],
        '6': [
            [1,1,1],
            [1,0,0],
            [1,1,1],
            [1,0,1],
            [1,1,1]
        ],
        '7': [
            [1,1,1],
            [0,0,1],
            [0,0,1],
            [0,0,1],
            [0,0,1]
        ],
        '8': [
            [1,1,1],
            [1,0,1],
            [1,1,1],
            [1,0,1],
            [1,1,1]
        ],
        '9': [
            [1,1,1],
            [1,0,1],
            [1,1,1],
            [0,0,1],
            [1,1,1]
        ]
    }
    
    detected_digits = ""
    
    for x, y, w, h in valid_contours:
        char_region = resized[y:y+h, x:x+w]
        
        if h >= 20 and w >= 10:
            resized_char = cv2.resize(char_region, (3, 5), interpolation=cv2.INTER_AREA)
            binary_char = (resized_char > 127).astype(int)
            
            best_match = '?'
            best_score = 0
            
            for digit, pattern in digit_patterns.items():
                pattern_array = np.array(pattern)
                matches = np.sum(pattern_array == binary_char)
                score = matches / pattern_array.size
                
                if score > best_score and score > 0.6:
                    best_score = score
                    best_match = digit
            
            if best_match.isdigit():
                detected_digits += best_match
    
    score_digits = ""
    for char in detected_digits:
        if char.isdigit():
            score_digits += char
    
    if score_digits:
        return int(score_digits)
    
    return -1

def main():
    screen_region = (334, 299, 400, 700)
    
    with mss.mss() as sct:
        bbox = {'top': screen_region[1], 'left': screen_region[0], 
                'width': screen_region[2], 'height': screen_region[3]}
        
        games_played = 0
        current_score = 0
        last_game_over_state = False
        
        while True:
            start_time = time.time()
            
            frame = np.array(sct.grab(bbox))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            game_frame = frame[100:, :]
            
            birds = detect_bird(game_frame)
            pipes = detect_pipes(game_frame)
            gameover_boxes = detect_gameover(game_frame)
            
            extracted_score = extract_score_from_region(game_frame)
            if extracted_score >= 0:
                current_score = extracted_score
            
            game_over_detected = len(gameover_boxes) > 0
            
            if game_over_detected and not last_game_over_state:
                games_played += 1
            
            if not game_over_detected and last_game_over_state:
                current_score = 0
            
            last_game_over_state = game_over_detected
            
            if birds and pipes:
                bird_x, bird_y, bird_w, bird_h = birds[0]
                bird_left = bird_x
                bird_right = bird_x + bird_w
                
                pipe_groups = {}
                for pipe_x, pipe_y, pipe_w, pipe_h in pipes:
                    pipe_left = pipe_x
                    
                    group_found = False
                    for existing_x in list(pipe_groups.keys()):
                        if abs(pipe_left - existing_x) < 20:
                            pipe_groups[existing_x].append((pipe_x, pipe_y, pipe_w, pipe_h))
                            group_found = True
                            break
                    
                    if not group_found:
                        pipe_groups[pipe_left] = [(pipe_x, pipe_y, pipe_w, pipe_h)]
                
                for group_x, group_pipes in pipe_groups.items():
                    rightmost_pipe = max(group_pipes, key=lambda p: p[0] + p[2])
                    score_line_x = rightmost_pipe[0] + rightmost_pipe[2]
                    
                    top_pipe = min(group_pipes, key=lambda p: p[1])
                    bottom_pipe = max(group_pipes, key=lambda p: p[1])
                    
                    gap_start_y = top_pipe[1] + top_pipe[3]
                    gap_end_y = bottom_pipe[1]
                    
                    cv2.line(game_frame, (score_line_x, gap_start_y), (score_line_x, gap_end_y), (0, 255, 255), 2)
            
            score_boxes, score_region = detect_score_text(game_frame)
            
            cv2.rectangle(game_frame, (5, 5), (110, 35), (255, 255, 0), 2)
            cv2.putText(game_frame, "Score Region", (25, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 0), 1)
            
            for bird in birds:
                cv2.rectangle(game_frame, (bird[0], bird[1]), (bird[0] + bird[2], bird[1] + bird[3]), (255, 0, 0), 2)
                cv2.putText(game_frame, f"Bird: ({bird[0]}, {bird[1]})", (bird[0], bird[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            for pipe in pipes:
                cv2.rectangle(game_frame, (pipe[0], pipe[1]), (pipe[0] + pipe[2], pipe[1] + pipe[3]), (0, 255, 0), 2)
                cv2.putText(game_frame, f"Pipe: ({pipe[0]}, {pipe[1]})", (pipe[0], pipe[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            if gameover_boxes:
                for box in gameover_boxes:
                    cv2.rectangle(game_frame, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]), (0, 0, 255), 2)
                    cv2.putText(game_frame, f"Game Over: ({box[0]}, {box[1]})", (box[0], box[1] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            frame[0:100, :] = [50, 50, 50]
            cv2.rectangle(frame, (0, 0), (frame.shape[1], 100), (100, 100, 100), 2)
            cv2.putText(frame, f"Games: {games_played} | Score: {current_score}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"AI Detection Status: Running", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, f"FPS: {int(1/(time.time()-start_time)) if time.time()-start_time > 0 else 0}", (10, 85),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            
            frame[100:, :] = game_frame
            
            cv2.imshow('Flappy Bird Detection', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            end_time = time.time()
            frame_time = end_time - start_time
            
            target_fps = 60
            target_time = 1.0 / target_fps
            if frame_time < target_time:
                time.sleep(target_time - frame_time)
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
