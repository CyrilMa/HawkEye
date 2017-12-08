import cv2
import numpy as np

import lines
from config import path_to_ressources

lines.init_id()

# parameters
source_filename = "test_files/image660.png"

# homography smoothing
delta = 5
coeffs = [4, 4, 3, 2, 1, 1]  # coef 0, coef 1, etc
threshold_1 = 6  # tolerance to deviation from the mean
threshold_2 = 3  # tolerance to deviation from previous homography

print("computing source...")
source_img = cv2.imread(source_filename)
source_corners = lines.get_corners(source_img, show_process=True)


begin = 661  # 1782
end = 1290  # 2013

print("computing homographies...")
homographies = []

for i in range(begin, end):
    filename = path_to_ressources + "frame_by_frame_2D/image" + str(i) + ".png"
    img = cv2.imread(filename)
    homography = lines.get_homography(source_corners, filename, show_process=False)
    homographies.append(homography)


def squared_sum(a):
    ans = 0.0
    for i in range(3):
        for j in range(3):
            ans += a[i][j]**2
    return ans

print("getting rid of incoherent values...")
standard_homography = np.zeros((3, 3))

for i in range(len(homographies)):
    standard_homography += homographies[i]

standard_homography /= len(homographies)

std = 0.0

for i in range(len(homographies)):
    std += squared_sum(homographies[i] - standard_homography)

std /= len(homographies)

count = 0
for i in range(len(homographies)):
    if squared_sum(homographies[i]-standard_homography) > threshold_1*std:
        count += 1
        if i > 0:
            homographies[i] = homographies[i-1]
        else:
            homographies[i] = homographies[i+1]

print("number of homographies that were removed (threshold_1): ")
print(count)

print("getting rid of values with too much difference relatively to previous frame...")
standard_diff = 0.0

for i in range(len(homographies)-1):
    standard_diff += squared_sum(homographies[i]-homographies[i+1])

standard_diff /= len(homographies) - 1

count = 0
for i in range(1, len(homographies)):
    if squared_sum(homographies[i]-homographies[i-1]) > threshold_2*standard_diff:
        count += 1
        homographies[i] = homographies[i-1]


print("number of homographies that were removed (threshold_2): ")
print(count)

print("computing warped images...")

for i in range(begin+delta, end-delta):
    homography = np.zeros((3, 3))

    for j in range(i-delta, i+delta+1):
        homography += homographies[j-begin]*coeffs[abs(j-i)]

    homography /= (delta*2+1)

    filename = path_to_ressources + "frame_by_frame_2D/image" + str(i) + ".png"
    img = cv2.imread(filename)
    warped = cv2.warpPerspective(img, homography, (img.shape[1], img.shape[0]))
    cv2.imwrite(path_to_ressources + "stabilized/image" + str(i) + ".png", warped)
