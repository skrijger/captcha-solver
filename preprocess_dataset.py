import os
import cv2
import scipy.ndimage
import numpy as np

def remove_circles(img):
    circles = cv2.HoughCircles(img, method = cv2.HOUGH_GRADIENT, dp = 1, minDist = 1, param1 = 50, param2 = 5, minRadius = 0, maxRadius = 2)
    return circles

def draw_circles(circles, img):
    circles = circles[0]
    for circle in circles:
        x = circle[0]
        y = circle[1]
        r = circle[2]
        img = cv2.circle(img, (x, y), r, (255), 2)
    return img

def nonzero_intervals(vec):
    if len(vec)==0:
        return []
    elif not isinstance(vec, np.ndarray):
        vec = np.array(vec)

    edges, = np.nonzero(np.diff((vec==0)*1))
    edge_vec = [edges+1]
    if vec[0] != 0:
        edge_vec.insert(0, [0])
    if vec[-1] != 0:
        edge_vec.append([len(vec)])
    edges = np.concatenate(edge_vec)
    return zip(edges[::2], edges[1::2])

img_path = os.path.join("captchas", "0V18.jpg")
print(img_path)
img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
ret, img = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)
circles0 = remove_circles(img)
cv2.imshow("img", img)

erosion = ~img
erosion = cv2.erode(erosion, np.ones((2, 2), np.uint8), iterations = 1)
erosion = ~erosion
erosion = scipy.ndimage.median_filter(erosion, (5, 1))
erosion = scipy.ndimage.median_filter(erosion, (1, 3))
erosion2 = scipy.ndimage.median_filter(erosion, (1, 5))
erosion = cv2.erode(erosion, np.ones((2, 2), np.uint8), iterations = 1)
erosion2 = cv2.erode(erosion2, np.ones((2, 2), np.uint8), iterations = 1)
erosion3 = scipy.ndimage.median_filter(erosion, (3, 3))

circles1 = remove_circles(erosion3)
if circles1 is not None:
    erosion3 = draw_circles(circles1, erosion3)

erosion3 = cv2.dilate(erosion3, np.ones((3, 3), np.uint8), iterations = 1) #scipy.ndimage.median_filter(erosion3, (3, 3, 3))
erosion3 = scipy.ndimage.median_filter(erosion3, (5, 1))
erosion3 = cv2.erode(erosion3, np.ones((3, 3), np.uint8), iterations = 2)
erosion3 = cv2.dilate(erosion3, np.ones((3, 3), np.uint8), iterations = 1)
cv2.imshow("final product", erosion3)

print(erosion3.shape)
col_sums = erosion3.shape[0] - (erosion3.sum(axis = 0) / 255)
print(col_sums.shape)
print(col_sums)
idx = np.argpartition(col_sums, -5)
print(idx[:5])
print(col_sums[idx[:5]])

cv2.imwrite("test.jpg", erosion3)

count = 0
marg = None
x = None
y = None
margIndex = None
intervals = []
erosion3 = cv2.cvtColor(erosion3, cv2.COLOR_GRAY2RGB)
for start, end in nonzero_intervals(col_sums):
    count += 1
    print(start, end)
    intervals.append([start, end])
    if marg is None or (end-start) > marg:
        margIndex = count-1
        marg = end-start
        x = start
        y = end
if count < 4: # 4 characters
    endLengths = int(marg * .25) # only consider candidates in the middle 50% of the interval, so remove the two 25% tails
    newX = x + endLengths
    newY = y - endLengths
    offset = np.argmin(col_sums[newX : newY])
    print("new intervals: ({}, {}), ({}, {})".format(x, newX+offset, newX+offset, y))
    intervals[margIndex] = [x, newX+offset]
    intervals.append([newX+offset, y])
for interval in intervals:
    start = interval[0]
    end = interval[1]
    cv2.line(erosion3, (start, 0), (start, img.shape[1]), (0, 0, 255), thickness=1, lineType=8)
    cv2.line(erosion3, (end, 0), (end, img.shape[1]), (0, 0, 255), thickness=1, lineType=8)
cv2.imshow("seg erosion", erosion3)

# optional -- i think it produces better output than above "final product"
'''erosion3 = ~(~img - (erosion3))
erosion3 = cv2.GaussianBlur(erosion3, (3, 3), sigmaX = 1)
kernel = np.array([[-1,-1,-1], [-1,10,-1], [-1,-1,-1]])
erosion3 = cv2.filter2D(erosion3, -1, kernel)
erosion3 = cv2.erode(erosion3, np.ones((2, 2), np.uint8), iterations = 1)
cv2.imshow("masked", erosion3)'''

'''erosion3 = ~erosion3
ws_erode = cv2.erode(erosion3, np.ones((2, 2), np.uint8), iterations = 6)
cv2.imshow("erode before watershed", ws_erode)
ret, markers1 = cv2.connectedComponents(ws_erode, 8)
markers1 = markers1+1
print(markers1)
old_erosion3 = ~erosion3
markers1[(~erosion3)==255] = 0
print(markers1)
print(np.unique(markers1))
erosion3 = cv2.cvtColor(erosion3, cv2.COLOR_GRAY2RGB)
markers = cv2.watershed(erosion3, markers1)
markers[old_erosion3==255] = -1
erosion3[markers == -1] = [0, 255, 0]
erosion3[markers == 1] = [255, 0, 255]
erosion3[markers == 2] = [0, 255, 255]
erosion3[markers == 3] = [0, 0, 255]
erosion3[markers == 4] = [255, 0, 0]
print(markers)
print(np.unique(markers))
cv2.imshow("watershed", erosion3)'''

'''contours, hierarchy = cv2.findContours(erosion3, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
erosion3 = cv2.drawContours(erosion3, contours, -1, (120), 2)
print("num contours: {}".format(len(contours)))
print(contours)
print(hierarchy)
cv2.imshow("contours", erosion3)'''

cv2.waitKey(0)