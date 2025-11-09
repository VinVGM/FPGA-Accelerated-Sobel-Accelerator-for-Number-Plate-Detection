# =============================================
# 1️⃣ Import Libraries and Load Overlay
# =============================================
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract

# =============================================
# 2️⃣ Load Input Image
# =============================================
try:
    img = cv2.imread("car3.png")
    # --- IMPORTANT ---
    # Resize the original image to match your hardware dimensions
    HW_IMG_WIDTH = 1000
    HW_IMG_HEIGHT = 467
    img = cv2.resize(img, (HW_IMG_WIDTH, HW_IMG_HEIGHT))
    
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title("Original Image (Resized)")
    plt.show()
except Exception as e:
    print(f"Error loading image: {e}")

# =============================================
# 3️⃣ Send Image to FPGA for Sobel Edge Detection
# =============================================
print("Loading FPGA result...")
fpga_result = cv2.imread("output.png", cv2.IMREAD_GRAYSCALE)
if fpga_result is None:
    raise Exception("Could not load 'output.png'.")
        
plt.imshow(fpga_result, cmap='gray')
plt.title("Hardware Sobel Edges (output.png)")
plt.show()

print("FPGA result loaded. ✅")

# =============================================
# 4️⃣ Plate Detection (CPU using FPGA result)
# =============================================

# =============================================
# 4️⃣ Plate Detection (CPU using FPGA result)
# =============================================

# Threshold the edge map to get clean, binary edges
thresh_value = 50
_ , binary_edges = cv2.threshold(fpga_result, thresh_value, 255, cv2.THRESH_BINARY)
plt.imshow(binary_edges, cmap='gray')
plt.title("Thresholded FPGA Edges")
plt.show()

# Find contours
contours, _ = cv2.findContours(binary_edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# --- Let's check more contours, just in case ---
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:20] 

plate = None
print("--- CONTOUR DEBUG REPORT ---")
print("Idx | Area   | Approx Sides | Aspect Ratio | Status")
print("-------------------------------------------------------")

for i, c in enumerate(contours):
    # Get area
    area = cv2.contourArea(c)
    
    # --- Filter out tiny noise early ---
    if area < 50:
        continue 
        
    # Get bounding box (x, y, width, height)
    (x, y, w, h) = cv2.boundingRect(c)
    
    # Calculate aspect ratio (avoid division by zero)
    aspect_ratio = float(w) / h if h > 0 else 0
    
    # Approximate the contour
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.018 * peri, True)
    approx_sides = len(approx)

    # Default status
    status = "Rejected"
    
    # Check our filters
    if approx_sides == 4 and aspect_ratio > 2.0 and aspect_ratio < 4.5 and area > 100:
        plate = approx
        status = "✅✅✅ FOUND! ✅✅✅"
    elif approx_sides != 4:
        status = "Rejected (Wrong # of sides)"
    elif area <= 100:
        status = "Rejected (Too small)"
    elif not (aspect_ratio > 2.0 and aspect_ratio < 4.5):
        status = f"Rejected (Bad aspect ratio: {aspect_ratio:.2f})"
    
    # Print the report line
    print(f" {i:2d} | {area:<6.0f} | {approx_sides:<12d} | {aspect_ratio:<12.2f} | {status}")
    
    if plate is not None:
        break
        
print("-------------------------------------------------------")


# Handle case where no 4-sided contour is found
if plate is None:
    print("Could not find a rectangular plate contour.")
else:
    # --- (Rest of your code is correct) ---
    print("Plate contour found!")
    gray_original = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = np.zeros(gray_original.shape, np.uint8)
    new_image = cv2.drawContours(mask, [plate], 0, 255, -1)
    new_image = cv2.bitwise_and(img, img, mask=mask)

    plt.imshow(cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB))
    plt.title("Detected Plate Area")
    plt.show()

    # =============================================
    # 5️⃣ Crop and OCR
    # =============================================
    # (Rest of your script is unchanged)
    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    
    cropped = gray_original[topx:bottomx+1, topy:bottomy+1]

    plt.imshow(cropped, cmap='gray')
    plt.title("Cropped Number Plate")
    plt.show()
    
    cropped = cv2.threshold(cropped, 120, 255, cv2.THRESH_BINARY_INV)[1]

    try:
        text = pytesseract.image_to_string(cropped, config='--psm 8')
        print("🚗 Detected Number Plate:", text.strip())
    except Exception as e:
        print(f"Pytesseract error: {e}")