import cv2
import numpy as np
import lines_3d
from scipy.optimize import minimize

source_filename = "test_files_3/foo-1704.jpeg"
source_img = cv2.imread(source_filename)
# cv2.imshow("my image", source_img)
# cv2.waitKey()

y1 = 0
y2 = 720
x1 = 0
x2 = 640
x3 = 1780

coordinates_3d = {
    "upper_left": [0, 11.85, 0, 1],
    "upper_right": [8.23, 11.85, 0, 1],
    "bottom_left": [0, 0, 0, 1],
    "bottom_right": [8.23, 0, 0, 1],
    "middle_left": [0, 5.435, 0, 1],
    "middle_right": [8.23, 5.435, 0, 1],
    "fond_left": [0., 23.77, 0, 1],
    "fond_right": [8.23, 23.77, 0, 1]
}

im_left = source_img[y1:y2, x1:x2]
# cv2.imshow("left image", im_left)
# cv2.waitKey()

im_right = source_img[y1:y2, x2:x3]
# cv2.imshow("right image", im_right)
# cv2.waitKey()


def homogene(x):
    ans = x.copy()
    for i in range(len(x)):
        ans[i] = x[i]/x[-1]
    return ans


def loss_p(p, object_points, im_points):
    ans = 0.
    temp = np.reshape(p, (3, 4))

    for i in range(len(object_points)):
        current = np.matmul(temp, object_points[i])
        current = np.sum(np.array([1, 5, 0])*(im_points[i]-homogene(current))**2)
        ans += current
    return ans


def get_projection(im1, im2):
    corners1 = lines_3d.get_corners(im1, show_process=True)
    corners2 = lines_3d.get_corners(im2, show_process=False)
    print(corners1)
    print(corners2)
    image_points1 = []
    image_points2 = []
    object_points = []

    for key in coordinates_3d.keys():
        image_points1.append(corners1[key])
        image_points2.append(corners2[key])
        object_points.append(coordinates_3d[key])

    image_points1 = np.array(image_points1).astype('float32')
    image_points2 = np.array(image_points2).astype('float32')
    object_points = np.array(object_points).astype('float32')

    p0 = np.ones(12)*0.01

    p1 = minimize(loss_p, p0, args=(object_points, image_points1), method='powell', options={'disp': True})
    p1 = p1["x"]
    p1 = np.reshape(p1, (3, 4))

    p0 = np.ones(12)*0.01

    p2 = minimize(loss_p, p0, args=(object_points, image_points2), method='powell', options={'disp': True})
    p2 = p2["x"]
    p2 = np.reshape(p2, (3, 4))

    return p1, p2


def loss(x, m1=np.array([14, 575, 1]), m2=np.array([25, 575, 1])):
    xp = np.ones(4)
    xp[:-1] = x

    # print(m1)
    # print(homogene(np.matmul(p1, xp)))
    # print("")
    # print(m2)
    # print(homogene(np.matmul(p2, xp)))
    # print("")

    ans = np.sum((m1-homogene(np.matmul(p1, xp)))**2)
    ans += np.sum((m2-homogene(np.matmul(p2, xp)))**2)

    return ans


p1, p2 = get_projection(im_left, im_right)


projected_point1 = np.matmul(p1, np.array([8.23, 11.85, 0, 1]))
projected_point2 = np.matmul(p2, np.array([8.23, 11.85, 0, 1]))

for i in range(3):
    projected_point1[i] /= projected_point1[2]
    projected_point2[i] /= projected_point2[2]

print(projected_point1)
print(projected_point2)


print(loss(np.array([0, 0, 0]), np.array([14, 575, 1]), np.array([25, 575, 1])))

x0 = np.array([0, 0, 0])
res = minimize(loss, x0, method='powell', options={'disp': True})

print(res)



















