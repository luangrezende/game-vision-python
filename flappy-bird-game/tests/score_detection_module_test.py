import cv2
import numpy as np
import sys
import os
import mss
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules'))
from score_detection_module import ScoreDetector

def main():
    detector = ScoreDetector()
    
    sct = mss.mss()
    capture_region = {
        "top": 275,
        "left": 520,
        "width": 400,
        "height": 700
    }
    
    frame_count = 0
    start_time = time.time()
    last_score = -1
    last_bbox = None
    ocr_times = []
    ocr_count = 0
    
    try:
        while True:
            screenshot = sct.grab(capture_region)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            annotated_frame = frame.copy()
            
            frame_count += 1
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:
                fps = frame_count / elapsed_time
                cv2.putText(annotated_frame, "FPS: ", (10, 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.putText(annotated_frame, f"{fps:.1f}", (55, 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            if frame_count % 60 == 0:
                ocr_start = time.time()
                score, bbox = detector.extract_score_with_ocr(frame)
                ocr_end = time.time()
                
                ocr_time = (ocr_end - ocr_start) * 1000
                ocr_times.append(ocr_time)
                ocr_count += 1
                
                if bbox is not None:
                    last_score = score
                    last_bbox = bbox
            
            if last_bbox is not None:
                x, y, w, h = last_bbox
                cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                label_text = "Score section"
                color = (0, 255, 0)
                cv2.putText(annotated_frame, label_text, (x, y + h + 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            if last_score >= 0:
                cv2.putText(annotated_frame, "Score: ", (10, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.putText(annotated_frame, f"{last_score}", (70, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            if ocr_times:
                avg_ocr_time = sum(ocr_times[-10:]) / min(len(ocr_times), 10)
                cv2.putText(annotated_frame, "OCR: ", (280, 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.putText(annotated_frame, f"{avg_ocr_time:.1f}ms", (325, 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            cv2.imshow('Flappy Bird Score Detection', annotated_frame)
            
            cv2.pollKey()
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except Exception as e:
        pass
    
    finally:
        detector.cleanup()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
