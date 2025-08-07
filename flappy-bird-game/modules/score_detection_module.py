import cv2
import numpy as np
import easyocr
import re

class ScoreDetector:
    def __init__(self):
        import torch
        
        if not torch.cuda.is_available():
            raise RuntimeError("GPU not available but required. Install PyTorch with CUDA.")
        
        self.reader = easyocr.Reader(['pt', 'en'], gpu=True, verbose=False)
        self.last_valid_score = -1
        self.last_valid_bbox = None
        
    def extract_score_with_ocr(self, frame):
        h, w = frame.shape[:2]
        
        score_region_height = 150
        score_region_width = 400
        
        start_y = max(0, 20)
        end_y = min(h, start_y + score_region_height)
        start_x = max(0, (w - score_region_width) // 2)
        end_x = min(w, start_x + score_region_width)
        
        roi = frame[start_y:end_y, start_x:end_x]
        
        scale_factor = 5
        roi_resized = cv2.resize(roi, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LANCZOS4)
        
        results = self.reader.readtext(
            roi_resized,
            text_threshold=0.1,
            width_ths=0.5,
            height_ths=0.5,
            min_size=5,
            detail=1
        )
        
        best_score_result = None
        best_confidence = 0
        
        for (bbox, text, confidence) in results:
            conf_value = float(confidence)
            
            score_match = re.search(r'score\s*:?\s*(\d+)', text, re.IGNORECASE)
            if score_match:
                score_value = int(score_match.group(1))
                if 0 <= score_value <= 99:
                    if conf_value > 0.1 and (best_score_result is None or conf_value > best_confidence):
                        points = np.array(bbox).astype(int)
                        points = points // scale_factor
                        
                        x = min(points[:, 0]) + start_x
                        y = min(points[:, 1]) + start_y
                        w = max(points[:, 0]) - min(points[:, 0])
                        h = max(points[:, 1]) - min(points[:, 1])
                        
                        best_score_result = (score_value, (x, y, w, h), conf_value)
                        best_confidence = conf_value
        
        if best_score_result:
            score, bbox, conf = best_score_result
            self.last_valid_score = score
            self.last_valid_bbox = bbox
            return score, bbox
        
        if self.last_valid_score >= 0:
            return self.last_valid_score, self.last_valid_bbox
        
        return -1, None
    
    def detect_and_draw_score(self, frame):
        annotated_frame = frame.copy()
        
        score, bbox = self.extract_score_with_ocr(frame)
        
        if bbox is not None:
            x, y, w, h = bbox
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            if score >= 0:
                label = f"Score: {score}"
                color = (0, 255, 0)
            else:
                label = "Score region"
                color = (0, 255, 255)
                
            cv2.putText(annotated_frame, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        return annotated_frame, score
    
    def cleanup(self):
        self.last_valid_score = -1
        self.last_valid_bbox = None
