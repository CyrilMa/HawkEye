import cv2
import numpy as np
import lines_3d

source_filename = "test_files_3/foo-1704.jpeg"

# size of image
y1 = 0
y2 = 720
x1 = 0
x2 = 640
x3 = 1780

coordinates_3d = {
    "upper_left": [0, 11.85, 0],
    "upper_right": [8.23, 11.85, 0],
    "bottom_left": [0, 0, 0],
    "bottom_right": [8.23, 0, 0],
    "middle_left": [0, 5.435, 0],
    "middle_right": [8.23, 5.435, 0],
    "fond_left": [0., 23.77, 0],
    "fond_right": [8.23, 23.77, 0]
}

source_img = cv2.imread(source_filename)
cv2.imshow("my image", source_img)
cv2.waitKey()

im_left = source_img[y1:y2, x1:x2]
cv2.imshow("left image", im_left)
cv2.waitKey()

im_right = source_img[y1:y2, x2:x3]
cv2.imshow("right image", im_right)
cv2.waitKey()


def get_projection(im):
    corners = lines_3d.get_corners(im, show_process=True)

    print("corners")
    print(corners)

    image_points = []
    object_points = []

    for key in coordinates_3d.keys():
        image_points.append(corners[key][:2])
        object_points.append(coordinates_3d[key])

    image_points = np.array(image_points).astype('float32')
    object_points = np.array(object_points).astype('float32')

    rms, camera_matrix, dist_coefs, rvecs, tvecs = cv2.calibrateCamera(
        [object_points],
        [image_points],
        (x2, y2),
        None,
        None
    )

    print("dist coefs")
    print(dist_coefs)

    print("rms")
    print(rms)

    rvecs = rvecs[0]
    tvecs = np.reshape(tvecs[0], 3)

    rotation, _ = cv2.Rodrigues(rvecs)

    r_t = np.zeros((3, 4))
    r_t[:, :3] = rotation
    r_t[:, 3] = tvecs

    return np.matmul(camera_matrix, r_t), camera_matrix, dist_coefs, corners

print("computing projection matrix for left image...")
p1, cm1, dc1, corners1 = get_projection(im_left)
print("\ncomputing projection matrix for right image...")
p2, cm2, dc2, corners2 = get_projection(im_right)

projected_point = np.matmul(p2, np.array([8.23, 11.85, 0, 1]))

for i in range(3):
    projected_point[i] /= projected_point[2]

print("trying to reproject 3D points into left image:")
print("expected 2D coordinates:")
print(corners2["upper_right"])
print("computed 2D coordinated")
print(projected_point)


print("\nchecking if triangulation works on the corners:")
for key in coordinates_3d.keys():
    left_point = np.array([[corners1[key][:2]]], dtype='float32')
    right_point = np.array([[corners2[key][:2]]], dtype='float32')

    # left_point = cv2.undistortPoints(left_point, cm1, dc1)
    # right_point = cv2.undistortPoints(right_point, cm2, dc2)

    # avec le undistort ca fait nimp...
    # et sans:
    #

    coordinates = cv2.triangulatePoints(p1, p2, left_point, right_point)

    coordinates = np.reshape(coordinates, 4)
    coordinates = coordinates.astype(dtype='float32')

    for i in range(4):
        coordinates[i] = coordinates[i]/float(coordinates[3])

    print(key)
    print("expected coordinates (approx):")
    print(coordinates_3d[key])
    print("triangulation coordinates")
    print(coordinates)
    print()

print("\nComputing 3D position of the ball")
left_point = np.array([[[429, 137]]], dtype='float32')
right_point = np.array([[[441, 137]]], dtype='float32')

# left_point = cv2.undistortPoints(left_point, cm1, dc1)
# right_point = cv2.undistortPoints(right_point, cm2, dc2)

ball = cv2.triangulatePoints(p1, p2, left_point, right_point)

ball = np.reshape(ball, 4)
ball = ball.astype(dtype='float32')

for i in range(4):
    ball[i] = ball[i] / float(ball[3])

print("expected coordinates (approx):")
print([7, 0, 2.5, 1])
print("triangulation coordinates")
print(ball)

