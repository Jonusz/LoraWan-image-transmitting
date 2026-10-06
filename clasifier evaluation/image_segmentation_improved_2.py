#!/usr/bin/env python3
import sys
import cv2
import numpy as np

def main():
    # 1. Check if the user provided an image path
    if len(sys.argv) < 2:
        print("ERROR: No image provided. Usage: ./segmentator.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    img = cv2.imread(image_path)
    if img is None:
        print(f"ERROR: Could not read image at {image_path}")
        sys.exit(1)

    # 2. Resize to 256x256 (Optimizes processing speed on RPi)
    img = cv2.resize(img, (256, 256))

    # 3. CLAHE Lighting Normalization (via LAB color space)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)
    
    merged_lab = cv2.merge((cl, a_channel, b_channel))
    clahe_img = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)

    # Convert the lighting-corrected image to HSV
    hsv = cv2.cvtColor(clahe_img, cv2.COLOR_BGR2HSV)

    # 4. Define the Color Anchors (H, S, V)
    anchors = {
        "00": np.array([45, 180, 150]),   # Green Areas (Earth/Vegetation)
        "01": np.array([105, 200, 240]),  # Blue Sky (Bright cyan/blue)
        "10": np.array([120, 150, 50]),   # Dark Sky / Water (Deep blue, low brightness)
        "11": np.array([0, 0, 255])       # Clouds / White (No color, max brightness)
    }

    # 5. Grid logic (8x8 = 64 cells). Image is 256, so cells are 32x32.
    cell_size = 32 
    bits = []

    # K-Means setup parameters
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 2 # Find the top 2 colors in the cell to eliminate minor noise

    for row in range(8):
        for col in range(8):
            # Extract the 32x32 square
            cell = hsv[row*cell_size : (row+1)*cell_size, col*cell_size : (col+1)*cell_size]

            # Flatten the cell to a 2D array of pixels for K-Means
            pixels = np.float32(cell.reshape((-1, 3)))

            # Run K-Means to find the color clusters
            _, labels, centers = cv2.kmeans(pixels, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

            # Find the most frequent cluster (the true dominant color)
            counts = np.bincount(labels.flatten())
            dominant_color = centers[np.argmax(counts)]

            # Measure Euclidean distance to each anchor
            shortest_distance = float('inf')
            winning_bits = "11"

            for bit_val, anchor_vector in anchors.items():
                distance = np.linalg.norm(dominant_color - anchor_vector)
                
                if distance < shortest_distance:
                    shortest_distance = distance
                    winning_bits = bit_val

            bits.append(winning_bits)

    # 6. Convert the 128 ones and zeros into a 32-character Hex string
    binary_string = "".join(bits)
    hex_value = hex(int(binary_string, 2))[2:].upper().zfill(32) 
    
    # 7. CRITICAL STEP: Print exactly what the ESP32 expects
    # The ESP32 code uses '<' and '>' to catch the UART transmission
    print(f"hex value: {hex_value}")

if __name__ == "__main__":
    main()