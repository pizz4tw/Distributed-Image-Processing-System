import cv2
import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def process_image(img, operation):
    if operation == 'edge_detection':
        return cv2.Canny(img, 100, 200)
    elif operation == 'color_inversion':
        return cv2.bitwise_not(img)
    elif operation == 'blurring':
        return cv2.GaussianBlur(img, (15, 15), 0)
    elif operation == 'median_filter':
        return cv2.medianBlur(img, 5)
    elif operation == 'brightness_up':
        return cv2.convertScaleAbs(img, alpha=1.2, beta=0)
    elif operation == 'brightness_down':
        return cv2.convertScaleAbs(img, alpha=0.8, beta=0)
    else:
        return img  # No operation

def process_images(images, operation):
    processed_results = []
    for image in images:
        img = cv2.imread(image, cv2.IMREAD_COLOR)
        if img is None:
            logging.error("Failed to load image: %s", image)
            processed_results.append(None)
        else:
            processed_img = process_image(img, operation)
            if processed_img is None:
                logging.error("Failed to process image: %s", image)
            else:
                processed_results.append(processed_img)
                processed_filename = os.path.join('/shared', os.path.splitext(os.path.basename(image))[0] + '_processed.jpg')
                cv2.imwrite(processed_filename, processed_img)
                logging.info("Image processed successfully on machine: %s", os.uname().nodename)
                logging.info("Saved processed image as: %s", processed_filename)

if __name__ == '__main__':
    operation = sys.argv[1]
    image_ids = sys.argv[2:]
    node_rank = int(os.getenv('OMPI_COMM_WORLD_RANK'))
    with open(f'/shared/chunk_{node_rank}.txt') as f:
        images = f.read().splitlines()
    process_images(images, operation)
