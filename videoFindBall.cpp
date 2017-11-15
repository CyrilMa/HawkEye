#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include "opencv2/opencv.hpp"
#include <iostream>
#include <fstream>

#include "maxflow/graph.h"
#include "graphCuts.hpp"


using namespace std;
using namespace cv;


int main() {

	Mat frame=imread("ressources/ts/ts4.png");
    Mat ball;
    namedWindow("ball",1);

    findBall(frame,ball);
    imshow("Result",ball);
    imshow("Frame",frame);

    waitKey(0);


    /**VideoCapture cap("ressources/video1.mp4"); // open the video
    VideoWriter outputVideo;

   if(!cap.isOpened())  // check if we succeeded
        return -1;

    if (!outputVideo.isOpened())
    {
        cout  << "Could not open the output video for write: " << source << endl;
        return -1;
    }


    namedWindow("ball",1);
    for(;;)
    {
        Mat frame;
        cap >> frame; // get a new frame from camera

        // Step 1 : Homograaphie pour "fixer" la camera


        // Step 2 : Traquer la balle dans l'image
        Mat ball;
        findBall(frame,ball);
        outputVideo << ball;
    } **/


}

