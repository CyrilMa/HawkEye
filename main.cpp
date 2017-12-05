#include <iostream>
#include <fstream>
#include <list>
#include "Eigen/Dense"

#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/opencv.hpp>

#include "maxflow/graph.h"
#include "graphCuts.hpp"



using namespace Eigen;
using namespace std;
using namespace cv;


void followBall(int from, int to, list<Point2i>& point_list, Mat& output, bool write = false) {
  char name[255];

  for(int i = from;i<=to;i++)
  {
      sprintf(name,"ressources/stabilized/image%d.png",i);
      Mat frame = imread(name,1);

      Mat ball;

      // Step 2 : Traquer la balle dans l'image
      if(findBall(frame,ball)) {
          Point2i p = find_position(ball);
          circle(output,p,2,Scalar(0,255,0),2);
          point_list.push_back(p);
      }

      if(write) {
        sprintf(name,"ressources/output/image%d.png",i);
        imwrite(name,ball);
      }

  }

  return;
}

int main(int argc, char *argv[]) {
    // GC from to DEG_MAX
    int from = atoi(argv[1]);
    int to = atoi(argv[2]);
    int DEG_MAX = atoi(argv[3]);

    // Image qui servira de support visuel
    Mat output = imread("ressources/stabilized/image870.png",1);
    int n = output.cols; int m = output.rows;

    // On repère la balle dans l'image
    list<Point2i> point_list;
    followBall(from,to,point_list,output);

    // Par la méthode des moindres carrés on approxime la trajectoire de la balle
    MatrixXd X(point_list.size(),DEG_MAX);
    MatrixXd Y(point_list.size(),1);

    int i=0;
    for(list<Point2i>::iterator it=point_list.begin(); it != point_list.end(); ++it) {
        Y(i,0) = (float) (*it).y;
        float x = (float) (*it).x;
        for(int j=0;j<DEG_MAX; j++) X(i,j) = pow(x,j);
        i++;
    }

    MatrixXd beta(DEG_MAX,1);
    beta = (((X.transpose()*X).inverse())*X.transpose())*Y;

    // On trace la courbe obtenu par la regression polynomiale
    MatrixXd y_s(1,1);
    MatrixXd x_s(1,DEG_MAX);

    for(int i=0; i<n; i++) {
      for(int j=0;j<DEG_MAX;j++)
        x_s(0,j) = pow(i,j);
      y_s = x_s * beta;
      if(y_s(0,0)<m) output.at<Vec3b>((int) y_s(0,0),i) = Vec3b(0,0,255);
    }

    // Visualisation du résultat
    imshow("ball",output);waitKey(0);




}
