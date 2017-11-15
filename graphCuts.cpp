#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>

#include "maxflow/graph.h"
#include "graphCuts.hpp"
#include <list>

using namespace std;
using namespace cv;

// Distance arrangée du point à l'un des espaces 1=balle, 0=extérieru
float Dp(const Point& p, int i,  Mat& I){
    Vec3b color = I.at<Vec3b>(p);
    Vec3b color_src_sink[] = {Vec3b(81,115,199), Vec3b(134,220,255)};
    if(i==1) return 5*norm(color, color_src_sink[i], CV_L2);
    if(i==0) return norm(color, color_src_sink[i], CV_L2);
}

float g(float x){
    return 1./(1.+x*x);
}

float lambda(const Point& p,const Point& q, Mat& G){
    return (g(G.at<float>(p.y, p.x))+g(G.at<float>(q.y, q.x))) / 2;
}

bool is_white(Mat& M,int i,int j) {
    return(M.at<uchar>(i,j)==255);
}

void findBall(Mat& input, Mat& output) {


    Mat F;
    cvtColor(input,F,CV_BGR2GRAY);

    int m = input.rows;int n = input.cols;

    Mat G(m,n,CV_32F);
	for (int i=1;i<m-1;i++) {
		for (int j=1;j<n-1;j++){
            float ix=0; float iy=0;
            ix += -(float(F.at<uchar>(i-1,j-1)))+(float(F.at<uchar>(i-1,j+1)));
            ix += -2*(float(F.at<uchar>(i,j-1)))+2*(float(F.at<uchar>(i,j+1)));
            ix += -(float(F.at<uchar>(i+1,j-1)))+(float(F.at<uchar>(i+1,j+1)));

            iy += -(float(F.at<uchar>(i-1,j-1)))+(float(F.at<uchar>(i+1,j-1)));
            iy += -2*(float(F.at<uchar>(i-1,j)))+2*(float(F.at<uchar>(i+1,j)));
            iy += -(float(F.at<uchar>(i-1,j+1)))+(float(F.at<uchar>(i+1,j+1)));

			G.at<float>(i,j)=sqrt(ix*ix+iy*iy);
		}
    }

    Graph<float, float, float> g(m*n,4*m*n);
	g.add_node(m*n);

	for(int i=0;i<m;i++){
        for(int j=0; j<n;j++){
            int pos = i*n+j;
            g.add_tweights(pos, Dp(Point(j,i), 0, input), Dp(Point(j,i), 1, input));
        }
	}


	for(int i=0;i<m-1;i++){
        for (int j=0; j<n-1;j++){
            int pos = i*n+j;
            float h = lambda(Point(j,i), Point(j+1,i),G);
            float v = lambda(Point(j,i), Point(j,i+1),G);
            g.add_edge( pos, pos+1, h,h);
            g.add_edge( pos, pos+n, v,v);
        }
	}


	int flow = g.maxflow();
    output = F.clone();
    int color[] = {255,0};
    for (int i=0;i<m;i++) {
        for (int j=0;j<n;j++){
            output.at<uchar>(i,j) = color[g.what_segment(i*n+j)];
        }
    }
	return;
}

Point2i position(Mat& ball) {
    list<Point2i> white_pixels;
    int m=ball.rows; int n=ball.cols;

    for(int i=0;i<m;i++) {
        for(int j=0;j<n; j++)
            if(is_white(ball,i,j) && is_white(ball,i-1,j) && is_white(ball,i+1,j) && is_white(ball,i,j-1) && is_white(ball,i,j+1))
                white_pixels.push_front(Point2i(i,j));
    }

    int n_pixels = white_pixels.size();
    Point2i avg = Point2i(0,0);

    for(int i=0;i<n_pixels;i++) {
        Point2i p = white_pixels.back();
        avg = avg + p;
        white_pixels.pop_back();
    }

    avg = avg/n_pixels;
    return(avg);
}
