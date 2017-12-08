import cv2
import numpy as np

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

# parameters for line selection
bottom_delta = 30
middle_delta = 20

# parameters for line selection
window = [150, 400, 150, 400]


def get_horizontal_lines(lines):
    """
    :param lines: array of lines
    :return: the indexes corresponding the major horizontal lines in the image
    """
    max_y1_y2 = 0
    second_max_y1_y2 = 0
    third_max_y1_y2 = 0
    index_max = 0
    index_second_max = 0
    index_third_max = 0
    index_fourth_max = 0
    fourth_max_y1_y2 = 0

    # looking for bottom line
    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            if (x1-x2)**2 > (y1-y2)**2:
                if int((y1+y2)/2) > max_y1_y2:
                    max_y1_y2 = int((y1+y2)/2)
                    index_max = i

    # looking for middle line
    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            if (x1 - x2) ** 2 > (y1 - y2) ** 2:
                if max_y1_y2 - bottom_delta > int((y1+y2)/2) > second_max_y1_y2:
                    second_max_y1_y2 = int((y1+y2)/2)
                    index_second_max = i

    # looking for upper line (the line formed by the bottom of the net)
    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            if (x1 - x2) ** 2 > (y1 - y2) ** 2:
                if second_max_y1_y2 - middle_delta > int((y1+y2)/2) > third_max_y1_y2:
                    third_max_y1_y2 = int((y1+y2)/2)
                    index_third_max = i

    # looking for fond line
    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            if (x1 - x2) ** 2 > (y1 - y2) ** 2:
                if third_max_y1_y2 - middle_delta > int((y1+y2)/2) > fourth_max_y1_y2:
                    fourth_max_y1_y2 = int((y1+y2)/2)
                    index_fourth_max = i

    return index_max, index_second_max, index_third_max, index_fourth_max


def get_side_lines(lines):
    """
    :param lines
    :return: indexes of the most vertical lines
    """
    right_max_alpha = 0
    left_max_alpha = 0
    left_index = 0
    right_index = 0

    for i in range(len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            if x1 < x2:
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            try:
                current_alpha = (y1 - y2) ** 2 / (x1 - x2)**2
            except:
                continue
            if y2 > y1:
                if current_alpha > left_max_alpha:
                    left_max_alpha = current_alpha
                    left_index = i
            else:
                if current_alpha > right_max_alpha:
                    right_max_alpha = current_alpha
                    right_index = i

    return left_index, right_index


def get_intersection(line_1, line_2):
    """
    :param line_1: coordinates of two points from the line
    :param line_2: coordinates of two points from the line
    :return: coordinates of the intersection
    """
    for x1, y1, x2, y2 in line_1:
        m1 = (y1-y2)/(x1-x2)
        p1 = (y1*x2 - y2*x1)/(x2-x1)

    for x1, y1, x2, y2 in line_2:
        m2 = (y1-y2)/(x1-x2)
        p2 = (y1*x2 - y2*x1)/(x2-x1)

    x = (p1 - p2) / (m2 - m1)
    y = m1 * x + p1
    return [int(x), int(y), 1]


def get_corners_from_lines(left_line, right_line, bottom_line, upper_line, middle_line, fond_line):
    """
    :param left_line: coordinates of two points from the line
    ...
    :return: (dict) coordinates of the six intersection of the lines
    """
    return {
        "upper_left": get_intersection(left_line, upper_line),
        "upper_right": get_intersection(right_line, upper_line),
        "bottom_right": get_intersection(right_line, bottom_line),
        "bottom_left": get_intersection(left_line, bottom_line),
        "middle_left": get_intersection(left_line, middle_line),
        "middle_right": get_intersection(right_line, middle_line),
        "fond_left": get_intersection(left_line, fond_line),
        "fond_right": get_intersection(right_line, fond_line)
    }


def get_corners(img, show_process=False):
    """
    :param img: (opencv image)
    :param show_process: (bool) set to True if you want to show steps of the process
    :param print_process: (bool) set to True if you want to write steps if the process in a folder
    :return: (dict) coordinates of the corners of the tennis pitch
    """

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.blur(gray, ksize=kernel)
    edges = cv2.Canny(gray, canny_threshold, canny_threshold * canny_ratio, apertureSize=3)

    if show_process:
        cv2.imshow("Canny filter", edges)
        cv2.waitKey()

    lines = cv2.HoughLinesP(edges, rho, theta, threshold, minLineLength=minLineLength, maxLineGap=maxLineGap)

    if show_process:
        temp_img = img.copy()
        for i in range(len(lines)):
            for x1, y1, x2, y2 in lines[i]:
                cv2.line(temp_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.imshow('houghlines', temp_img)
        cv2.waitKey()

    bottom_line_index, middle_line_index, top_line_index, fond_line_index = get_horizontal_lines(lines)
    bottom_line = lines[bottom_line_index]
    upper_line = lines[top_line_index]
    middle_line = lines[middle_line_index]
    fond_line = lines[fond_line_index]

    left_line_index, right_line_index = get_side_lines(lines)
    left_line = lines[left_line_index]
    right_line = lines[right_line_index]

    if show_process:
        temp_img = img.copy()

        for x1, y1, x2, y2 in bottom_line:
            cv2.line(temp_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        for x1, y1, x2, y2 in upper_line:
            cv2.line(temp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        for x1, y1, x2, y2 in left_line:
            cv2.line(temp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        for x1, y1, x2, y2 in right_line:
            cv2.line(temp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        for x1, y1, x2, y2 in middle_line:
            cv2.line(temp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        for x1, y1, x2, y2 in fond_line:
            cv2.line(temp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        if show_process:
            cv2.imshow('houghlines', temp_img)
            cv2.waitKey()

    corners = get_corners_from_lines(left_line, right_line, bottom_line, upper_line, middle_line, fond_line)

    if show_process:
        temp_img = img.copy()

        for key in corners.keys():
            (x, y, h) = corners[key]
            cv2.circle(temp_img, (x, y), radius=4, color=(0, 255, 255), thickness=5)

        cv2.imshow('houghlines', temp_img)
        cv2.waitKey()

    return corners


# def ncc(i1, i2):
#     product = 0
#     for i in range(3):
#         current_i1 = i1[:, :, i]
#         current_i2 = i2[:, :, i]
#         product += np.mean((current_i1 - current_i1.mean()) * (current_i2 - current_i2.mean()))
#     stds = i1.std() * i2.std()
#     if stds == 0:
#         return 0
#     else:
#         product /= stds
#         return product
#
#
# def get_central_point(source_img, target_img):
#     n = target_img.shape[0]
#     m = target_img.shape[1]
#
#     n_big = source_img.shape[0]
#     m_big = source_img.shape[1]
#
#     delta_n_1 = int(n/2)
#     delta_n_2 = n - delta_n_1
#
#     delta_m_1 = int(m/2)
#     delta_m_2 = m - delta_m_1
#
#     best_ncc = 0
#     best_i = 0
#     best_j = 0
#
#     for i in range(window[0], window[1]):
#         for j in range(window[2], window[3]):
#             current = source_img[i - delta_n_1:i + delta_n_2, j - delta_m_1:j + delta_m_2]
#             current_ncc = ncc(current, target_img)
#             if current_ncc > best_ncc:
#                 best_ncc = current_ncc
#                 best_i = i
#                 best_j = j
#
#     current = source_img[best_i - delta_n_1:best_i + delta_n_2, best_j - delta_m_1:best_j + delta_m_2]
#     cv2.imshow("thats the best", current)
#     cv2.waitKey()
#     print("best_i")
#     print(best_i)
#     print("best_j")
#     print(best_j)
#
#     return best_j, best_i
