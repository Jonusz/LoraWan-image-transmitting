#!/usr/bin/env python3
import sys
import cv2
import numpy as np

def main():
    # 1. Check if the user provided an image path when running the script
    if len(sys.argv) < 2:
        print("ERROR: No image provided. Usage: ./segmentator.py <image_path>")
        sys.exit(1) # Exit with an error code

    image_path = sys.argv[1]
    
    # 2. Load the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"ERROR: Could not read image at {image_path}")
        sys.exit(1)

    # 3. Process the image (Resize and HSV conversion)
    img = cv2.resize(img, (400, 400))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define the color range (e.g., green for vegetation/forests)
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([140, 255, 255])
    lower_urban = np.array([0, 0, 30])
    upper_urban = np.array([179, 50, 160])
    
    # Create the mask (White pixels = match, Black pixels = no match)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_urban = cv2.inRange(hsv, lower_urban, upper_urban)

    # 4. Grid logic (8x8 = 64 cells)
    cell_size = 50 
    bits = []

    for row in range(8):
        for col in range(8):
            # Extract a 100x100 square from the mask
            cell_green = mask_green[row*cell_size : (row+1)*cell_size, col*cell_size : (col+1)*cell_size]
            cell_blue = mask_blue[row*cell_size : (row+1)*cell_size, col*cell_size : (col+1)*cell_size]
            cell_urban = mask_urban[row*cell_size : (row+1)*cell_size, col*cell_size : (col+1)*cell_size]

            # Count how many pixels matched our color
            white_pixels_green = cv2.countNonZero(cell_green)
            white_pixels_blue = cv2.countNonZero(cell_blue)
            white_pixels_urban = cv2.countNonZero(cell_urban)
            percentage_green = (white_pixels_green / 2500) * 100 # 100x100 = 10,000 total pixels
            percentage_blue = (white_pixels_blue / 2500) * 100 # 100x100 = 10,000 total pixels
            percentage_urban = (white_pixels_urban / 2500) * 100 # 100x100 = 10,000 total pixels

            '''
            # If more than 15% of this square is green, write '1', else '0'
            if percentage_green > 10 and percentage_blue < 10 and percentage_urban < 10:
                bits.append("00")
            elif percentage_blue > 10 and percentage_green < 10:
                bits.append("01")
            elif percentage_green > 5 and percentage_blue > 5:
                bits.append("10")
            else:
                bits.append("11")
            '''
            biggest = max(percentage_green, percentage_blue, percentage_urban)
            if biggest == percentage_green and percentage_green > 10:
                bits.append("00")
            elif biggest == percentage_blue and percentage_blue > 10:
                bits.append("01")
            elif biggest == percentage_urban and percentage_urban > 10:
                bits.append("10")
            else:
                bits.append("11")

    # 5. Convert the 16 ones and zeros into a 4-character Hex string
    binary_string = "".join(bits)
    hex_value = hex(int(binary_string, 2))[2:].upper().zfill(32) 
    
    # 6. CRITICAL STEP: Print ONLY the hex value to standard output
    print("binary string: " + binary_string)
    print("hex value: " + hex_value)

if __name__ == "__main__":
    main()