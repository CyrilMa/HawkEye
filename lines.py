import cv2
import numpy as np

from config import path_to_ressources, default_print_process

# parameters:
# blur parameters
kernel = (3, 3)

# parameters for Canny filter
canny_threshold = 60
canny_ratio = 3

# HoughLines parameters
minLineLength = 150
maxLineGap = 200
rho = 1
theta = (np.pi/180)/2
threshold = 220

# parameters to eliminate parasite lines
top_margin = 150
bottom_margin = 20
left_margin = 100
right_margin = 100

top_delta = 40
right_delta = 40
left_delta = 40
bottom_delta = 40

# size of images
max_y = 720
max_x = 1280


def init_id():
    """
    just a way to have an incremental id
    """
    f = open("id.txt", 'w')
    f.write(str(1))
    f.close()


def get_id():
    """
    just a way to have an incremental id
    """
    f = open("id.txt", 'r')
    k = f.read()
    f.close()
    f = open("id.txt", 'w')
    f.write(str(int(k)+1))
    f.close()
    return k


def get_bottom_line(lines):
    """
    :param lines
    :return: index of the biggest line among the lines the horizontal lines at the bottom of the image
    """
    max_y1_y2 = 0
    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            if (x1-x2)**2 > 5*(y1-y2)**2:
                if max_y - bottom_margin > int((y1+y2)/2) > max_y1_y2:
                    max_y1_y2 = int((y1+y2)/2)

    index = 0
    max_line_size = 0
    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            if (x1-x2)**2 > 5*(y1-y2)**2:
                if max_y1_y2 + bottom_delta > int((y1+y2)/2) > max_y1_y2 - bottom_delta:
                    line_size = (x1 - x2) ** 2 + (y1 - y2) ** 2
                    if line_size > max_line_size:
                        max_line_size = line_size
                        index = i
    return index


def get_upper_line(lines):
    """
    :param lines
    :return: index of the biggest line among the lines the horizontal lines at the top of the image
    """
    min_y1_y2 = max_y
    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            if (x1-x2)**2 > 5*(y1-y2)**2:
                if top_margin < int((y1+y2)/2) < min_y1_y2:
                    min_y1_y2 = int((y1+y2)/2)

    index = 0
    max_line_size = 0
    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            if (x1-x2)**2 > 5*(y1-y2)**2:
                if min_y1_y2 - top_delta < int((y1+y2)/2) < min_y1_y2 + top_delta:
                    line_size = (x1 - x2) ** 2 + (y1 - y2) ** 2
                    if line_size > max_line_size:
                        max_line_size = line_size
                        index = i
    return index


def get_side_lines(lines):
    """
    :param lines
    :return: indexes of the biggest lines among the vertical lines on the sides of the image
    """
    min_x1_x2 = max_x
    max_x1_x2 = 0

    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            if (x1-x2)**2 < 5*(y1-y2)**2:
                if left_margin < int((x1+x2)/2) < min_x1_x2:
                    min_x1_x2 = int((x1+x2)/2)
                if max_x - right_margin > int((x1+x2)/2) > max_x1_x2:
                    max_x1_x2 = (x1+x2)/2

    index_left = 0
    max_line_size_left = 0
    index_right = 0
    max_line_size_right = 0

    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            if (x1-x2)**2 < 5*(y1-y2)**2:
                line_size = (x1 - x2) ** 2 + (y1 - y2) ** 2

                if min_x1_x2 - left_delta < int((x1+x2)/2) < min_x1_x2 + left_delta:
                    if line_size > max_line_size_left:
                        max_line_size_left = line_size
                        index_left = i

                if max_x1_x2 + right_delta > int((x1+x2)/2) > max_x1_x2 - right_delta:
                    if line_size > max_line_size_right:
                        max_line_size_right = line_size
                        index_right = i

    return index_left, index_right


def get_intersection(line_1, line_2):
    """
    :param line_1: coordinates of two points from the line
    :param line_2: coordinates of two points from the line
    :return: coordinates of the intersection
    """
    # on va mettre au format y = mx + p
    for x1, y1, x2, y2 in line_1:
        m1 = (y1-y2)/(x1-x2)
        p1 = (y1*x2 - y2*x1)/(x2-x1)

    for x1, y1, x2, y2 in line_2:
        m2 = (y1-y2)/(x1-x2)
        p2 = (y1*x2 - y2*x1)/(x2-x1)

    x = (p1 - p2) / (m2 - m1)
    y = m1 * x + p1

    return int(x), int(y)


def get_corners_from_lines(left_line, right_line, bottom_line, upper_line):
    """
    :param left_line: coordinates of two points from the line
    :param right_line: coordinates of two points from the line
    :param bottom_line: coordinates of two points from the line
    :param upper_line: coordinates of two points from the line
    :return: (dict) coordinates of the four intersection of the lines
    """
    return {
        "upper_left": get_intersection(left_line, upper_line),
        "upper_right": get_intersection(right_line, upper_line),
        "bottom_right": get_intersection(right_line, bottom_line),
        "bottom_left": get_intersection(left_line, bottom_line)
    }


def get_corners(img, show_process=False, print_process=default_print_process):
    """
    :param img: (opencv image)
    :param show_process: (bool) set to True if you want to show steps of the process
    :param print_process: (bool) set to True if you want to write steps if the process in a folder
    :return: (dict) coordinates of the corners of the tennis pitch
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # in this set of images, bluring makes a line disappear so we deactivate it
    # gray = cv2.blur(gray, ksize=kernel)
    edges = cv2.Canny(gray, canny_threshold, canny_threshold*canny_ratio, apertureSize=3)

    if show_process:
        cv2.imshow("Canny filter", edges)
        cv2.waitKey()

    lines = cv2.HoughLinesP(edges, rho, theta, threshold, minLineLength=minLineLength, maxLineGap=maxLineGap)

    if show_process or print_process:
        temp_img = img.copy()
        for i in range(len(lines)):
            for x1, y1, x2, y2 in lines[i]:
                cv2.line(temp_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if show_process:
            cv2.imshow('houghlines', temp_img)
            cv2.waitKey()

        if print_process:
            k = get_id()
            cv2.imwrite(path_to_ressources + '/houghlines/' + str(k) + ".png", temp_img)

    bottom_line = lines[get_bottom_line(lines)]
    upper_line = lines[get_upper_line(lines)]
    left_line_index, right_line_index = get_side_lines(lines)
    left_line = lines[left_line_index]
    right_line = lines[right_line_index]

    if show_process or print_process:
        temp_img = img.copy()

        for x1, y1, x2, y2 in bottom_line:
            cv2.line(temp_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        for x1, y1, x2, y2 in upper_line:
            cv2.line(temp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        for x1, y1, x2, y2 in left_line:
            cv2.line(temp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        for x1, y1, x2, y2 in right_line:
            cv2.line(temp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        if show_process:
            cv2.imshow('houghlines', temp_img)
            cv2.waitKey()

        if print_process:
            k = get_id()
            cv2.imwrite(path_to_ressources + '/houghlines/' + str(k) + ".png", temp_img)

    corners = get_corners_from_lines(left_line, right_line, bottom_line, upper_line)

    if show_process:
        temp_img = img.copy()

        for key in corners.keys():
            (x, y) = corners[key]
            cv2.circle(temp_img, (x, y), radius=4, color=(0, 255, 255), thickness=5)

        cv2.imshow('houghlines', temp_img)
        cv2.waitKey()

    return corners


def get_homography(source_corners, filename, show_process=False):
    """
    :param source_corners: (dict) coordinates of the corners from the source image
    :param filename: (str) path of the image to process
    :param show_process: (bool) set to True if you want the process to be displayed
    :return: (numpy array) homography that links the source image to the input image
    """
    img = cv2.imread(filename)
    new_corners = get_corners(img, show_process=show_process)

    src = []
    for key in source_corners.keys():
        (x, y) = source_corners[key]
        src.append([x, y])

    dst = []
    for key in new_corners.keys():
        (x, y) = new_corners[key]
        dst.append([x, y])

    src = np.array(src, dtype="float32")
    dst = np.array(dst, dtype="float32")

    homography = cv2.getPerspectiveTransform(dst, src)

    return homography


# def get_rectangle(corners, bottom_line, upper_line):
#     for x1, y1, x2, y2 in bottom_line:
#         alpha = -float((y1 - y2)) / (x1 - x2)
#         if abs(alpha) < 0.0001:
#             alpha = 0.0001
#         x_bottom_left, y_bottom_left = corners["bottom_left"]
#         y_left = y_bottom_left + (100 - x_bottom_left) / alpha
#         x_bottom_right, y_bottom_right = corners["bottom_right"]
#         y_right = y_bottom_right + (100 - x_bottom_right) / alpha
#         new_upper_left = get_intersection(np.array([[x_bottom_left, y_bottom_left, 100, y_left]]), upper_line)
#         new_upper_right = get_intersection(np.array([[x_bottom_right, y_bottom_right, 100, y_right]]), upper_line)
#
#         return {
#             "upper_left": new_upper_left,
#             "upper_right": new_upper_right,
#             "bottom_right": corners["bottom_right"],
#             "bottom_left": corners["bottom_left"]
#         }
