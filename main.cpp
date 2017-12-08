#include <iostream>
#include <fstream>
#include <vector>
#include "Eigen/Dense"

#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/opencv.hpp>

#include "maxflow/graph.h"
#include "graphCuts.hpp"

using namespace Eigen;
using namespace std;
using namespace cv;


void followBall(int from, int to, vector<Point2i>& point_list, Mat& output, bool write = false) {
  char name[255];

  for(int i = from;i<=to;i++)
  {
      cout<<i;

      sprintf(name,"ressources/stabilized/image%d.png",i);
      Mat frame = imread(name,1);

      Mat ball;

      // Step 2 : Traquer la balle dans l'image
      if(findBall(frame,ball)) {
          Point2i p = find_position_gaussian_blur(ball);
          if(p.x>0) {
            circle(output,p,2,Scalar(0,255,0),2);
            point_list.push_back(p); }
      }

      if(write) {
        sprintf(name,"ressources/output/image%d.png",i);
        imwrite(name,ball);
      }

  }

  return;
}

vector<Point2i>& removeOutliers(Mat& output,vector<Point2i>& point_list, float t = 5) {
    double avg = 0;
    vector<Point2i> * without_outliers = new vector<Point2i>;
    for(int i=2; i<point_list.size()-2; i++)
        avg = avg + pow(norm(point_list[i+1]-point_list[i]),2)+pow(norm(point_list[i-1]-point_list[i]),2)+pow(norm(point_list[i+2]-point_list[i]),2)+pow(norm(point_list[i-2]-point_list[i]),2);
    avg = avg/(point_list.size()-4);
    cout<<avg<<endl;
    for(int i=2;i<point_list.size()-2;i++) {
        if(pow(norm(point_list[i+1]-point_list[i]),2)+pow(norm(point_list[i-1]-point_list[i]),2)+pow(norm(point_list[i+2]-point_list[i]),2)+pow(norm(point_list[i-2]-point_list[i]),2)<t*avg)
            (*without_outliers).push_back(point_list[i]);
        else circle(output,point_list[i],2,Scalar(128,128,128),2);

    }
    return(*without_outliers);

}

int main(int argc, char *argv[]) {
    // GC from to DEG_MAX
    int from = atoi(argv[1]);
    int to = atoi(argv[2]);
    int DEG_MAX = atoi(argv[3]);

    // Image qui servira de support visuel
    char name[255];
    sprintf(name,"ressources/stabilized/image%d.png",from);
    Mat output = imread(name,1);
    int n = output.cols; int m = output.rows;

    // On repère la balle dans l'image
    vector<Point2i> point_list;
    followBall(from,to,point_list,output,true);
    point_list = removeOutliers(output,point_list,3);
    int N = point_list.size();
    cout<<N;
  // Par la méthode des moindres carrés on approxime la trajectoire de la balle
    MatrixXd X(N,DEG_MAX);
    MatrixXd Y(N,1);

    int i=0;
    for(vector<Point2i>::iterator it=point_list.begin(); it != point_list.end(); ++it) {

        Y(i,0) = (float) (*it).y;
        float x = (float) (*it).x;
        for(int j=0;j<DEG_MAX; j++) X(i,j) = pow(x,j);
        i++;
    }

    double best_score = DBL_MAX;
    int lim_pix;int best_i;

   for(int i=DEG_MAX; i<N-DEG_MAX; i++) {
        MatrixXd Xav = X.block(0,0,i,DEG_MAX);
        MatrixXd Xap = X.block(i,0,N-i,DEG_MAX);

        MatrixXd Yav = Y.block(0,0,i,1);
        MatrixXd Yap = Y.block(i,0,N-i,1);

        MatrixXd beta_av = (((Xav.transpose()*Xav).inverse())*Xav.transpose())*Yav;
        MatrixXd beta_ap = (((Xap.transpose()*Xap).inverse())*Xap.transpose())*Yap;

        double score = (Yav-Xav*beta_av).squaredNorm() + (Yap-Xap*beta_ap).squaredNorm();

        if(score<best_score) {
            best_score=score;
            lim_pix = point_list[i].x;
            best_i = i;
        }
    }


    MatrixXd beta_av_best(DEG_MAX,1);
    MatrixXd beta_ap_best(DEG_MAX,1);

    MatrixXd Xav = X.block(0,0,best_i,DEG_MAX);
    MatrixXd Xap = X.block(best_i,0,N-best_i,DEG_MAX);

    MatrixXd Yav = Y.block(0,0,best_i,1);
    MatrixXd Yap = Y.block(best_i,0,N-best_i,1);

    beta_av_best = (((Xav.transpose()*Xav).inverse())*Xav.transpose())*Yav;
    beta_ap_best = (((Xap.transpose()*Xap).inverse())*Xap.transpose())*Yap;

    // On trace la courbe obtenu par la regression polynomiale
    MatrixXd y_sav(1,1);MatrixXd y_sap(1,1);
    MatrixXd x_s(1,DEG_MAX);

    for(int i=0; i<n; i++) {
      for(int j=0;j<DEG_MAX;j++)
        x_s(0,j) = pow(i,j);

      y_sav = x_s * beta_av_best;
      if(y_sav(0,0)<m && y_sav(0,0)>0) output.at<Vec3b>((int) y_sav(0,0),i) = Vec3b(0,0,255);

      y_sap = x_s * beta_ap_best;
      if(y_sap(0,0)<m && y_sap(0,0)>0) output.at<Vec3b>((int) y_sap(0,0),i) = Vec3b(255,0,0);

      if((y_sav(0,0) -y_sap(0,0))*(y_sav(0,0) -y_sap(0,0))<1) circle(output,Point2i(i,(int) y_sap(0,0) ),2,Scalar(0,255,255),2);

    }

    // Visualisation du résultat
    imshow("ball",output);waitKey(0);




}
