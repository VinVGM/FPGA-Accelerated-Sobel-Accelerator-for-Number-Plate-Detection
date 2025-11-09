from PIL import Image
import sys

# --- Configuration ---
# These MUST match the parameters in your Verilog testbench
IMG_WIDTH = 1000
IMG_HEIGHT = 467

INPUT_HEX_FILE = "output.hex"    # Your output from the simulation
OUTPUT_IMAGE_FILE = "output.png" # The viewable image you want to create
# --- End Configuration ---

# Create a new, blank grayscale image
# "L" mode is for 8-bit grayscale
img = Image.new("L", (IMG_WIDTH, IMG_HEIGHT))
pixels = img.load()

print(f"Opening '{INPUT_HEX_FILE}'...")
try:
    with open(INPUT_HEX_FILE, "r") as f:
        hex_lines = f.readlines()

    # Check if we have the right number of pixels
    # Note: Your testbench only writes pixels when out_valid is high.
    # The first 2 rows/cols are invalid, so we expect fewer pixels.
    # We will fill the image starting from (2, 2)
    
    # Fill the image with black first (for the borders)
    for y in range(IMG_HEIGHT):
        for x in range(IMG_WIDTH):
            pixels[x, y] = 0

    print(f"Read {len(hex_lines)} valid pixels from hex file.")
    print("Reconstructing image...")

    # Iterate through the valid pixels and place them
    # in the image, offsetting by (2, 2)
    pixel_index = 0
    for y in range(2, IMG_HEIGHT):
        for x in range(2, IMG_WIDTH):
            if pixel_index < len(hex_lines):
                # Read the line, remove newline, and convert from hex
                hex_val = hex_lines[pixel_index].strip()
                pixel_val = int(hex_val, 16)
                
                # Set the pixel value in the image
                pixels[x, y] = pixel_val
                pixel_index += 1

    # 4. Save the final image
    img.save(OUTPUT_IMAGE_FILE)

    print("\n--- Success! ---")
    print(f"Created '{OUTPUT_IMAGE_FILE}'.")
    print("Open this file to see the result of your Sobel filter!")

except FileNotFoundError:
    print(f"ERROR: File not found: '{INPUT_HEX_FILE}'")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)