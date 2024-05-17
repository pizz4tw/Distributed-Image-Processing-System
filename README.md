# Distributed-Image-Processing-System
A distributed image processing system that runs on a cluster of computers on the cloud using AWS EC2 services.
This system assumes you already set-up an EC2 Cluster environment between master and slave nodes, if you don't know how you can refer to this link : https://blog.glennklockwood.com/2013/04/quick-mpi-cluster-setup-on-amazon-ec2.html
After setting up the environment you can run the scripts as guided below.


# Image_Server.py
The main node (master) running which has a Flask server to receive the user photo uploads.
To run this script it needs to have the templates folder in the same directory 
