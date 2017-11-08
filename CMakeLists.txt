cmake_minimum_required(VERSION 2.8.12.20131009)

SET(OpenCV_STATIC OFF)
FIND_PACKAGE(OpenCV REQUIRED)

PROJECT(Projet)

set(SOURCE_FILES main.cpp)
add_executable(main ${SOURCE_FILES})

INCLUDE_DIRECTORIES(${OpenCV_INCLUDE_DIRS})
