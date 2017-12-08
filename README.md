In order to run this project, you should first download the ressources folder here: 
link

You can put the folder anywhere, just make sure you change the paths to the folder in the config.py file and the paths in the main.cpp file.

requirements for python can be found in the requirements.txt file (you can run 'pip install -r requirements.txt')

First run the warp_images.py file. This stabilizes the images and stores them in the ressources/stabilized folder. If you set the default_print_process variable to True, it will also store the line selection process in the houglines folder.

Note: the stabilized images are already in the google drive repository so you can also skip this step.

Then you can run the main.cpp (adjust to your setup).

cmake CMakeLists.txt -G "Unix Makefiles"

make GC

./GC 802 866 3

check the report for more information about the code and how to use it.
