import cv2
import numpy as np

# A required dummy function for OpenCV sliders
def nothing(x):
    pass

def main():
    # 1. Load your test image
    image_path = 'image.png' # CHANGE THIS to your picture's name
    img = cv2.imread(image_path)
    
    if img is None:
        print(f"Error: Could not find {image_path}")
        return
        
    # Resize it so it fits nicely on your screen
    img = cv2.resize(img, (600, 600))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 2. Create a window with Sliders (Trackbars)
    cv2.namedWindow('HSV Tuner')
    cv2.resizeWindow('HSV Tuner', 400, 300)

    # Arguments: Slider Name, Window Name, Default Value, Max Value, Function
    cv2.createTrackbar('Hue Min', 'HSV Tuner', 35, 179, nothing)
    cv2.createTrackbar('Sat Min', 'HSV Tuner', 50, 255, nothing)
    cv2.createTrackbar('Val Min', 'HSV Tuner', 50, 255, nothing)
    cv2.createTrackbar('Hue Max', 'HSV Tuner', 85, 179, nothing)
    cv2.createTrackbar('Sat Max', 'HSV Tuner', 255, 255, nothing)
    cv2.createTrackbar('Val Max', 'HSV Tuner', 255, 255, nothing)

    print("Sliders opened! Tune the colors. Press 'q' to quit.")

    while True:
        # 3. Read the current position of all 6 sliders
        h_min = cv2.getTrackbarPos('Hue Min', 'HSV Tuner')
        s_min = cv2.getTrackbarPos('Sat Min', 'HSV Tuner')
        v_min = cv2.getTrackbarPos('Val Min', 'HSV Tuner')
        h_max = cv2.getTrackbarPos('Hue Max', 'HSV Tuner')
        s_max = cv2.getTrackbarPos('Sat Max', 'HSV Tuner')
        v_max = cv2.getTrackbarPos('Val Max', 'HSV Tuner')

        # 4. Create the arrays and the mask based on slider positions
        lower_bound = np.array([h_min, s_min, v_min])
        upper_bound = np.array([h_max, s_max, v_max])
        
        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        # 5. Show the original image and the black/white mask
        cv2.imshow('Original Image', img)
        cv2.imshow('Black & White Mask', mask)

        # 6. Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n--- Copy these arrays into your main code ---")
            print(f"lower_bound = np.array([{h_min}, {s_min}, {v_min}])")
            print(f"upper_bound = np.array([{h_max}, {s_max}, {v_max}])")
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()