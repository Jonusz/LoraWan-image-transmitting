import os
import glob
import shutil
import subprocess
import pandas as pd

# Paths and filenames
INPUT_DIR = "frames_from_video"
OUTPUT_DIR = "evaluation_results"
EXCEL_OUTPUT = "classifier_results.xlsx"

SCRIPT_C1 = "image_segmentation_improved_2.py"
SCRIPT_C2 = "image_segmentation_improved.py"
SCRIPT_DECODER = "decoder8.py"


def get_hex(script_name, img_path):
    """Runs a classifier script and extracts the 32-character hex value."""
    result = subprocess.run(
        ["python", script_name, img_path],
        capture_output=True,
        text=True
    )
    for line in result.stdout.splitlines():
        if "hex value:" in line:
            return line.split("hex value:")[1].strip()
    return None


def run_decoder(hex_value, final_dest_path):
    """Calls decoder8.py and moves its hardcoded output to the correct folder."""
    # Run the decoder (which creates 'reconstructed_8x8.jpg' in the main folder)
    subprocess.run(
        ["python", SCRIPT_DECODER, hex_value],
        capture_output=True,
        text=True
    )
    
    # The name of the file your decoder ALWAYS creates
    hardcoded_output = "reconstructed_8x8.jpg" 
    
    # Check if the decoder successfully made the file, then move and rename it!
    if os.path.exists(hardcoded_output):
        shutil.move(hardcoded_output, final_dest_path)
    else:
        print(f"Error: decoder8.py failed to create {hardcoded_output}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Supported image formats
    image_paths = sorted(
        glob.glob(os.path.join(INPUT_DIR, "*.jpg")) + 
        glob.glob(os.path.join(INPUT_DIR, "*.png"))
    )

    if not image_paths:
        print(f"No images found in '{INPUT_DIR}'!")
        return

    excel_data = []

    for img_path in image_paths:
        file_name = os.path.basename(img_path)
        base_name, _ = os.path.splitext(file_name)
        
        # 1. Create a dedicated folder for this frame
        target_folder = os.path.join(OUTPUT_DIR, base_name)
        os.makedirs(target_folder, exist_ok=True)

        # 2. Copy the original photo into the folder
        original_dest = os.path.join(target_folder, file_name)
        shutil.copy(img_path, original_dest)

        # 3. Run Classifier 1 & decode
        hex1 = get_hex(SCRIPT_C1, img_path)
        if hex1:
            c1_out_img = os.path.join(target_folder, "classifier1_grid.png")
            run_decoder(hex1, c1_out_img)
        else:
            print(f"Warning: Classifier 1 failed on {file_name}")

        # 4. Run Classifier 2 & decode
        hex2 = get_hex(SCRIPT_C2, img_path)
        if hex2:
            c2_out_img = os.path.join(target_folder, "classifier2_grid.png")
            run_decoder(hex2, c2_out_img)
        else:
            print(f"Warning: Classifier 2 failed on {file_name}")

        # 5. Append row data for Excel
        excel_data.append({
            "Photo Name": file_name,
            "Classifier 1 Hex": hex1 if hex1 else "ERROR",
            "Classifier 2 Hex": hex2 if hex2 else "ERROR"
        })

        print(f"Processed: {file_name}")

    # 6. Save results to Excel
    df = pd.DataFrame(excel_data)
    df.to_excel(EXCEL_OUTPUT, index=False)
    print(f"\nDone! Aggregated hex values saved to '{EXCEL_OUTPUT}'.")
    print(f"Individual photo packages saved in '{OUTPUT_DIR}/'.")


if __name__ == "__main__":
    main()