import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract

# --- CONFIGURATION ---
HW_IMG_WIDTH = 1000
HW_IMG_HEIGHT = 467
# ---------------------

# 1. Load Images
try:
    img_orig = cv2.imread("car3.png")
    img = cv2.resize(img_orig, (HW_IMG_WIDTH, HW_IMG_HEIGHT))
    
    # Load the edge map produced by your Verilog hardware
    edges = cv2.imread("output.png", cv2.IMREAD_GRAYSCALE)
    
    if edges is None:
        raise Exception("Could not load 'output.png'. Make sure it's in the same folder.")
        
    plt.imshow(edges, cmap='gray')
    plt.title("Hardware Sobel Edges (Original)")
    plt.show()

except Exception as e:
    print(f"Error loading images: {e}")
    exit()

# -----------------------------------------------------------------
# --- NEW FIX: THRESHOLDING ---
# Convert your grayscale magnitude map into a binary image
# to make it similar to the output from cv2.Canny.
#
# Pixels brighter than 'thresh_value' become 255 (white)
# Pixels dimmer than 'thresh_value' become 0 (black)
thresh_value = 50  # *** You can experiment with this value (e.g., 30, 70) ***
_ , binary_edges = cv2.threshold(edges, thresh_value, 255, cv2.THRESH_BINARY)

plt.imshow(binary_edges, cmap='gray')
plt.title(f"Hardware Edges after Thresholding (>{thresh_value})")
plt.show()
# -----------------------------------------------------------------


# 2. Detect Plate Area (using Hardware Edges)

# --- MODIFIED ---
# Find contours using the new 'binary_edges'
contours, _ = cv2.findContours(binary_edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

plate = None
for c in contours:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.018 * peri, True)
    if len(approx) == 4:  # Plate is likely a 4-sided polygon
        plate = approx
        break

# 3. Crop Plate Region
# (This section is the same as before)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

if plate is None:
    print("No plate contour found.") # If you still see this, try a different 'thresh_value'
else:
    mask = np.zeros(gray.shape, np.uint8)
    new_image = cv2.drawContours(mask, [plate], 0, 255, -1)
    new_image = cv2.bitwise_and(img, img, mask=mask)

    plt.imshow(cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB))
    plt.title("Detected Plate Area")
    plt.show()

    # Crop the detected region from the grayscale image
    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    cropped = gray[topx:bottomx+1, topy:bottomy+1]

    plt.imshow(cropped, cmap='gray')
    plt.title("Cropped Number Plate")
    plt.show()

    # 4. OCR (Extract Text)
    text = pytesseract.image_to_string(cropped, config='--psm 8')
    print("🚗 Detected Number Plate:", text.strip())