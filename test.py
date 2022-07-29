# example command:
# python -i test-3.jpg

import cv2
import argparse
import time

from easyocr import Reader

def cleanup_text(text: str) -> str:
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()

# image = cv2.imread("test-1.jpg", cv2.IMREAD_COLOR)
# image = cv2.imread("test-2.jpg", cv2.IMREAD_COLOR)
# image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# image = cv2.GaussianBlur(src=image, ksize=(3, 3), sigmaX=0, sigmaY=0)
# clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(12, 12))
# image = clahe.apply(image)
# _, image = cv2.threshold(image, thresh=165, maxval=255, type=cv2.THRESH_TRUNC + cv2.THRESH_OTSU)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image to be OCR'd")
ap.add_argument("-l", "--langs", type=str, default="en",
	help="comma separated list of languages to OCR")
ap.add_argument("-g", "--gpu", type=int, default=1,
	help="whether or not GPU should be used")
args = vars(ap.parse_args())

# break the input languages into a comma separated list
langs = args["langs"].split(",")
print("[INFO] OCR'ing with the following languages: {}".format(langs))

# load the input image from disk
image = cv2.imread(args["image"])
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
image = cv2.GaussianBlur(src=image, ksize=(3, 3), sigmaX=0, sigmaY=0)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(12, 12))
image = clahe.apply(image)
_, image = cv2.threshold(image, thresh=165, maxval=255, type=cv2.THRESH_TRUNC + cv2.THRESH_OTSU)
image = cv2.resize(image, (640, 360), interpolation=cv2.INTER_LINEAR)

# OCR the input image using EasyOCR
print("[INFO] OCR'ing input image...")
start = time.time()
reader = Reader(langs, gpu=args["gpu"] > 0)
results = reader.readtext(image)
print("execution time: %.2f seconds" % (time.time() - start))

# loop over the results
for (bbox, text, prob) in results:
	# display the OCR'd text and associated probability
	# print("[INFO] {:.4f}: {}".format(prob, text))
	print("{}".format(text))
	# # unpack the bounding box
	# (tl, tr, br, bl) = bbox
	# tl = (int(tl[0]), int(tl[1]))
	# tr = (int(tr[0]), int(tr[1]))
	# br = (int(br[0]), int(br[1]))
	# bl = (int(bl[0]), int(bl[1]))
	# # cleanup the text and draw the box surrounding the text along
	# # with the OCR'd text itself
	# text = cleanup_text(text)
	# cv2.rectangle(image, tl, br, (0, 255, 0), 2)
	# cv2.putText(image, text, (tl[0], tl[1] - 10),
	# 	cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

cv2.imshow("image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()