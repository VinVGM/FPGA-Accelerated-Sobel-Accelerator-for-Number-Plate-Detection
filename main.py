import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract




# 1. Load the Image
try:
    img = cv2.imread("car.png")
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title("Original Image")
    plt.show()
except Exception as e:
    print(f"Error loading image: {e}")
    print("Make sure 'car.jpg' is in your jupyter_notebooks folder.")


# 2. Detect Plate Area
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.bilateralFilter(gray, 11, 17, 17) # Noise reduction
edges = cv2.Canny(gray, 30, 200) # Edge detection

plt.imshow(cv2.cvtColor(edges, cv2.COLOR_BGR2RGB))
plt.title("graya")
plt.show()

# Find contours
contours, _ = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

plate = None
for c in contours:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.018 * peri, True)
    if len(approx) == 4:  # Plate is likely a 4-sided polygon
        plate = approx
        break

# 3. Crop Plate Region
if plate is None:
    print("No plate contour found.")
else:
    mask = np.zeros(gray.shape, np.uint8)
    new_image = cv2.drawContours(mask, [plate], 0, 255, -1)
    new_image = cv2.bitwise_and(img, img, mask=mask)

    plt.imshow(cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB))
    plt.title("Detected Plate Area")
    plt.show()

    # Crop the detected region
    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    cropped = gray[topx:bottomx+1, topy:bottomy+1]

    plt.imshow(cropped, cmap='gray')
    plt.title("Cropped Number Plate")
    plt.show()

    # 4. OCR (Extract Text)
    # --psm 8 assumes a single word.
    text = pytesseract.image_to_string(cropped, config='--psm 8')
    print("🚗 Detected Number Plate:", text.strip())