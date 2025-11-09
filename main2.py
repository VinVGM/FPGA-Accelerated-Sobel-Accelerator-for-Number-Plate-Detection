from PIL import Image
import sys

# --- Configuration ---
# These MUST match the parameters in your Verilog files
IMG_WIDTH = 1000
IMG_HEIGHT = 467

# Specify your input and output files
INPUT_IMAGE_FILE = "car.png"  # Change this to your image's name
OUTPUT_HEX_FILE = "image.hex"      # The output file for the testbench
# --- End Configuration ---

try:
    # 1. Open the image
    print(f"Opening '{INPUT_IMAGE_FILE}'...")
    img = Image.open(INPUT_IMAGE_FILE)

    # 2. Resize to the exact dimensions for the hardware
    print(f"Resizing image to {IMG_WIDTH}x{IMG_HEIGHT}...")
    # Use LANCZOS (formerly ANTIALIAS) for better quality resizing
    img_resized = img.resize((IMG_WIDTH, IMG_HEIGHT), Image.Resampling.LANCZOS)

    # 3. Ensure image is in RGB format (removes alpha channel etc.)
    img_rgb = img_resized.convert("RGB")

    # 4. Write to the hex file
    print(f"Writing pixel data to '{OUTPUT_HEX_FILE}'...")
    
    total_pixels = 0
    with open(OUTPUT_HEX_FILE, "w") as f:
        # Iterate over pixels row by row (y), then column by column (x)
        for y in range(IMG_HEIGHT):
            for x in range(IMG_WIDTH):
                # Get the (R, G, B) tuple
                r, g, b = img_rgb.getpixel((x, y))
                
                # Format as a 24-bit RRGGBB hex string
                hex_value = f"{r:02x}{g:02x}{b:02x}"
                
                # Write to file with a newline
                f.write(hex_value + "\n")
                total_pixels += 1

    print("--- Success! ---")
    print(f"Created '{OUTPUT_HEX_FILE}' with {total_pixels} pixels ({IMG_WIDTH}x{IMG_HEIGHT}).")
    print("You can now use this 'image.hex' file in EDA Playground.")

except FileNotFoundError:
    print(f"ERROR: Input file not found: '{INPUT_IMAGE_FILE}'")
    print("Please make sure the file is in the same directory as the script.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)