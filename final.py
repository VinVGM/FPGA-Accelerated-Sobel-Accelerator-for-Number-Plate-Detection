
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract

try:
    img = cv2.imread("car.png")

    HW_IMG_WIDTH = 1000
    HW_IMG_HEIGHT = 467
    img = cv2.resize(img, (HW_IMG_WIDTH, HW_IMG_HEIGHT))
    
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title("Original Image (Resized)")
    plt.show()
except Exception as e:
    print(f"Error loading image: {e}")


print("Loading FPGA result...")
fpga_result = cv2.imread("output.png", cv2.IMREAD_GRAYSCALE)
if fpga_result is None:
    raise Exception("Could not load 'output.png'.")
        
plt.imshow(fpga_result, cmap='gray')
plt.title("Hardware Sobel Edges (output.png)")
plt.show()

print("FPGA result loaded. ✅")



thresh_value = 50
_ , binary_edges = cv2.threshold(fpga_result, thresh_value, 255, cv2.THRESH_BINARY)
plt.imshow(binary_edges, cmap='gray')
plt.title("Thresholded FPGA Edges")
plt.show()


contours, _ = cv2.findContours(binary_edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:20] 

plate = None
print("Searching for plate-like contours...")


for c in contours:

    (x, y, w, h) = cv2.boundingRect(c)
    

    aspect_ratio = float(w) / h if h > 0 else 0
    

    area = cv2.contourArea(c)
    

    if aspect_ratio > 2.0 and aspect_ratio < 4.5 and area > 1000:

        plate = c 
        print(f"Found potential plate with aspect ratio: {aspect_ratio:.2f}")
        break



# Handle case where no plate is found
if plate is None:
    print("Could not find a plate-like contour.")
else:
    # --- (Rest of your code is correct) ---
    print("Plate contour found!")
    gray_original = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # We create the mask by drawing the *entire contour* (c)
    mask = np.zeros(gray_original.shape, np.uint8)
    cv2.drawContours(mask, [plate], 0, 255, -1) 
    
    # Apply the mask to the original color image
    new_image = cv2.bitwise_and(img, img, mask=mask)

    plt.imshow(cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB))
    plt.title("Detected Plate Area")
    plt.show()

    # =============================================
    # 5️⃣ Crop and OCR
    # =============================================
    # (This section is unchanged and will now work)
    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    print(topx , " " , bottomx , " " , topy ," " , bottomy)
    cropped = gray_original[topx:bottomx+1, topy:bottomy+1]

    


   