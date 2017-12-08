#ifndef GRAPHCUTS_HPP_INCLUDED
#define GRAPHCUTS_HPP_INCLUDED

#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>
#include "maxflow/graph.h"

using namespace std;
using namespace cv;

float Dp(const Point& p, int i,  Mat& I);
float g(float x);
float lambda(const Point& p,const Point& q, Mat& G);
bool is_white(Mat& M,int i,int j);

bool findBall(Mat& input, Mat& output);
Point2i find_position(Mat& ball);
Point2i find_position_gaussian_blur(Mat& ball) ;

#endif // GRAPHCUTS_HPP_INCLUDED
