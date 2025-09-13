"""
OCR service for extracting text from certificate images
"""

import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Optional, Dict, Any
import io
import requests
from app.core.config import settings

class OCRService:
    def __init__(self):
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """Extract text from certificate image"""
        try:
            # Load image
            image = self._load_image(image_path)
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image)
            
            # Extract text using Tesseract
            raw_text = pytesseract.image_to_string(
                processed_image,
                lang=settings.OCR_LANGUAGES,
                config='--psm 6'
            )
            
            # Extract structured data
            structured_data = self._extract_structured_data(raw_text)
            
            return {
                "raw_text": raw_text.strip(),
                "structured_data": structured_data,
                "confidence": self._get_confidence_score(processed_image),
                "success": True
            }
            
        except Exception as e:
            return {
                "raw_text": "",
                "structured_data": {},
                "confidence": 0.0,
                "success": False,
                "error": str(e)
            }

    def _load_image(self, image_path: str) -> np.ndarray:
        """Load image from file or URL"""
        if image_path.startswith(('http://', 'https://')):
            response = requests.get(image_path)
            image = Image.open(io.BytesIO(response.content))
        else:
            image = Image.open(image_path)
        
        return np.array(image)

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply thresholding
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply morphological operations
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return processed

    def _extract_structured_data(self, text: str) -> Dict[str, str]:
        """Extract structured data from raw OCR text"""
        structured_data = {}
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Extract student name (look for patterns like "Name:", "Student Name:", etc.)
            if any(keyword in line.lower() for keyword in ['name:', 'student name:', 'candidate name:']):
                structured_data['student_name'] = self._extract_value_after_colon(line)
            
            # Extract roll number
            elif any(keyword in line.lower() for keyword in ['roll no:', 'roll number:', 'reg no:', 'registration no:']):
                structured_data['roll_number'] = self._extract_value_after_colon(line)
            
            # Extract marks/grade
            elif any(keyword in line.lower() for keyword in ['marks:', 'grade:', 'cgpa:', 'percentage:']):
                structured_data['marks'] = self._extract_value_after_colon(line)
            
            # Extract certificate number
            elif any(keyword in line.lower() for keyword in ['cert no:', 'certificate no:', 'certificate number:', 'serial no:']):
                structured_data['cert_number'] = self._extract_value_after_colon(line)
        
        return structured_data

    def _extract_value_after_colon(self, line: str) -> str:
        """Extract value after colon in a line"""
        if ':' in line:
            return line.split(':', 1)[1].strip()
        return line

    def _get_confidence_score(self, image: np.ndarray) -> float:
        """Get confidence score for OCR extraction"""
        try:
            data = pytesseract.image_to_data(
                image,
                lang=settings.OCR_LANGUAGES,
                output_type=pytesseract.Output.DICT
            )
            
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            if confidences:
                return sum(confidences) / len(confidences) / 100.0
            return 0.0
        except:
            return 0.0

    def extract_text_from_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """Extract text from image bytes"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image_array = np.array(image)
            return self.extract_text_from_image_array(image_array)
        except Exception as e:
            return {
                "raw_text": "",
                "structured_data": {},
                "confidence": 0.0,
                "success": False,
                "error": str(e)
            }

    def extract_text_from_image_array(self, image_array: np.ndarray) -> Dict[str, Any]:
        """Extract text from image array"""
        try:
            # Preprocess image
            processed_image = self._preprocess_image(image_array)
            
            # Extract text
            raw_text = pytesseract.image_to_string(
                processed_image,
                lang=settings.OCR_LANGUAGES,
                config='--psm 6'
            )
            
            # Extract structured data
            structured_data = self._extract_structured_data(raw_text)
            
            return {
                "raw_text": raw_text.strip(),
                "structured_data": structured_data,
                "confidence": self._get_confidence_score(processed_image),
                "success": True
            }
            
        except Exception as e:
            return {
                "raw_text": "",
                "structured_data": {},
                "confidence": 0.0,
                "success": False,
                "error": str(e)
            }
