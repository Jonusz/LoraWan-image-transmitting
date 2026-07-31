#!/usr/bin/env python3
import sys
import cv2
import numpy as np

def main():
    # 1. Check if the user provided a hex string
    if len(sys.argv) < 2:
        print("ERROR: No hex string provided. Usage: ./decoder.py <HEX_STRING>")
        sys.exit(1)

    hex_string = sys.argv[1]
    hex_string = hex_string.replace("<", "").replace(">", "")

    # 2. Convert Hex to a 32-bit binary string
    try:
        # zfill(32) ensures we have exactly 32 zeros and ones
        binary_string = bin(int(hex_string, 16))[2:].zfill(32)
    except ValueError:
        print(f"ERROR: '{hex_string}' is not a valid hexadecimal string.")
        sys.exit(1)

    print(f"Decoding Hex: {hex_string}")
    print(f"Binary map:   {binary_string}")

    # 3. Create a blank 400x400 image
    img_size = 400
    cell_size = 100
    img = np.zeros((img_size, img_size, 3), dtype=np.uint8)

    # 4. Loop through the 16 cells
    for i in range(16):
        # Because each cell is 2 bits, we multiply the index by 2 to grab the right chunk
        # Example: cell 0 gets bits 0-1, cell 1 gets bits 2-3, etc.
        bit_pair = binary_string[i*2 : i*2+2]
        
        row = i // 4
        col = i % 4
        
        x1 = col * cell_size
        y1 = row * cell_size
        x2 = x1 + cell_size
        y2 = y1 + cell_size
        
        # 5. Determine the color based on your specific encoding
        if bit_pair == '00':
            color = (0, 255, 0)     # OpenCV is BGR -> Solid Green
        elif bit_pair == '01':
            color = (255, 0, 0)     # OpenCV is BGR -> Solid Blue
        elif bit_pair == '10':
            color = (255, 255, 0)   # OpenCV is BGR -> Cyan/Teal (Mixed)
        else: # bit_pair == '11'
            color = (150, 150, 150) # Light Grey (Neither/Clouds)
            
        # Draw the filled rectangle for the cell
        cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)
        
        # Draw a white border around the cell for the grid
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 2)

    # 6. Save the resulting image
    output_filename = f"reconstructed_{hex_string}.jpg"
    cv2.imwrite(output_filename, img)
    print(f"Success! Reconstructed image saved as: {output_filename}")

    # Display it on your laptop screen
    #cv2.imshow("Balloon View Reconstruction", img)
    #cv2.waitKey(0) 
    #cv2.destroyAllWindows()

if __name__ == "__main__":
    main()