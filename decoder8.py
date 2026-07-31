#!/usr/bin/env python3
import sys
import cv2
import numpy as np

def main():
    # 1. Check if the user provided a hex string
    if len(sys.argv) < 2:
        print("ERROR: No hex string provided. Usage: ./decoder8.py <HEX_STRING>")
        sys.exit(1)

    hex_string = sys.argv[1]
    hex_string = hex_string.replace("<", "").replace(">", "")

    # 2. Convert Hex to a 128-bit binary string
    try:
        binary_string = bin(int(hex_string, 16))[2:].zfill(128)
    except ValueError:
        print(f"ERROR: '{hex_string}' is not a valid hexadecimal string.")
        sys.exit(1)

    print(f"Decoding Hex: {hex_string}")

    # 3. Create a blank 800x800 image
    img_size = 800
    cell_size = 100
    img = np.zeros((img_size, img_size, 3), dtype=np.uint8)

    # 4. Loop through the 64 cells
    for i in range(64):
        bit_pair = binary_string[i*2 : i*2+2]
        
        row = i // 8
        col = i % 8
        
        x1 = col * cell_size
        y1 = row * cell_size
        x2 = x1 + cell_size
        y2 = y1 + cell_size
        
        # 5. Determine color based on your specific 'max' logic
        if bit_pair == '00':
            color = (0, 255, 0)     # Solid Green (Vegetation)
        elif bit_pair == '01':
            color = (255, 0, 0)     # Solid Blue (Water)
        elif bit_pair == '10':
            color = (0, 0, 255)     # Solid Red (Urban/Streets)
        else: 
            color = (150, 150, 150) # Grey (Fallback/Clouds/Unknown)
            
        # Draw the filled rectangle for the cell
        cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)
        
        # Draw a white border around the cell for the grid
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 1)

    # 6. Save the resulting image
    output_filename = f"reconstructed_8x8.jpg"
    cv2.imwrite(output_filename, img)
    print(f"Success! Reconstructed image saved as: {output_filename}")

if __name__ == "__main__":
    main()