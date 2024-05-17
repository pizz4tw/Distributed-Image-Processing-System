# Distributed-Image-Processing-System
A distributed image processing system that runs on a cluster of computers on the cloud using AWS EC2 services.

# Prerequisites
OpenCV,Flask
```
sudo apt install -y python3-opencv 
sudo apt install -y python3-flask  
```
If any other modules are needed install it using:
```
sudo apt install -y python3-(package_name)
```
# Setting up the Cloud environment
This system assumes you already set-up an EC2 Cluster environment between master and slave nodes, if you don't know how you can refer to this link: 
https://blog.glennklockwood.com/2013/04/quick-mpi-cluster-setup-on-amazon-ec2.html

Make sure you modify the security groups (launch-wizardX) for the nodes to allow for HTTP requests on port 5000 from 0.0.0.0 (anywhere IPv4) also setup the /shared directory between the 3 machines using these commands:

#MASTER NODE 
```
sudo apt-get install nfs-kernel-server nfs-common
echo "/shared n2(rw,sync,no_subtree_check) n3(rw,sync,no_subtree_check)" | sudo tee -a /etc/exports
sudo exportfs -a
sudo systemctl restart nfs-kernel-server
```
#SLAVE NODE
```
sudo apt-get install nfs-common
sudo mkdir -p /shared
sudo mount (master_machine_name):/shared /shared
```
Now you should have a shared directory between the machines which they can communicate on and distribute the tasks between them.

After setting up the environment you can run the scripts as guided below.


# Image_Server.py
This script runs on the main node (master) which has a Flask web server that receives the user image uploads. (up to 50 tested on t3.micro free tier, 3 machines (1 master + 2 slaves))

-To run this script it needs to have the templates directory in the same directory as itself (templates directory must contain the "index.html" + "processing.html" files.)

-When the server is up and running the user can input the IPaddress:PORT (which in our case PublicIPaddressOfMaster:5000) in their web browser then they are greeted with a page that has an upload button to upload images and a dropdown menu in which they can select one of the image processing operations available which are (Canny Edge detector, Blurring(Gaussian), Median filter (for S&P noises) , Brightness Up/Down, Color negation(inversion)).

-After the button "Upload and Process" is pressed the user has to wait(until the upload is done and the server receives all the images) to be transfered to the next page where he is able to download the processed images as a zip file.

# slave_process.py
This script is put in the /shared directory where it is seen by all the machines and is the one responsible for the image processing and contains all the image processing operations mentioned above

You can also add more operations using the OpenCV library in python.

# del_jpg.sh
A simple shell script that runs after the user downloads the images as a zip file to free up space in the /shared directory by deleting all the (jpg,jpeg,png....etc) files.
NOTE: needs to be in the /shared directory too.

# End-User guide
-It is preferable to upload .jpg & .png files (.gif,.avif..etc. won't be handled correctly and may cause failures)

-Preferable to upload < 50 photos for complete results (no images will be missed in the processing step)
