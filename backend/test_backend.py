#!/usr/bin/env python3
"""
Test script for backend functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from helpers import get_available_filters, detect_person, apply_background_filter
import cv2
import numpy as np

def test_filters():
    """Test filter availability"""
    print("Testing filter availability...")
    filters = get_available_filters()
    print(f"Available filters: {len(filters)}")
    for filter_info in filters:
        print(f"  - {filter_info['name']}: {filter_info['description']}")
    print("✅ Filter test passed\n")

def test_person_detection():
    """Test person detection with a sample image"""
    print("Testing person detection...")
    
    # Create a simple test image (black background with a white rectangle representing a person)
    test_image = np.zeros((300, 400, 3), dtype=np.uint8)
    
    # Add a white rectangle to simulate a person
    cv2.rectangle(test_image, (150, 100), (250, 250), (255, 255, 255), -1)
    
    # Test person detection
    mask = detect_person(test_image)
    
    print(f"Mask shape: {mask.shape}")
    print(f"Mask unique values: {np.unique(mask)}")
    print("✅ Person detection test passed\n")

def test_background_filter():
    """Test background filter application"""
    print("Testing background filter...")
    
    # Create a simple test image
    test_image = np.zeros((300, 400, 3), dtype=np.uint8)
    
    # Add a white rectangle to simulate a person
    cv2.rectangle(test_image, (150, 100), (250, 250), (255, 255, 255), -1)
    
    # Add some colored background
    test_image[50:80, 50:150] = [0, 255, 0]  # Green
    test_image[200:230, 250:350] = [255, 0, 0]  # Red
    
    # Test grayscale filter
    filtered = apply_background_filter(test_image, 'grayscale')
    
    print(f"Original image shape: {test_image.shape}")
    print(f"Filtered image shape: {filtered.shape}")
    print("✅ Background filter test passed\n")

def main():
    """Run all tests"""
    print("🧪 Running backend tests...\n")
    
    try:
        test_filters()
        test_person_detection()
        test_background_filter()
        print("🎉 All tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
