# Distributed-Image-Processing-System
A distributed image processing system that runs on a cluster of computers on the cloud using AWS EC2 services.
This system assumes you already set-up an EC2 Cluster environment between master and slave nodes, if you don't know how you can refer to this link: 
https://blog.glennklockwood.com/2013/04/quick-mpi-cluster-setup-on-amazon-ec2.html

Make sure you modify the security groups to allow for HTTP requests on port 5000 from 0.0.0.0 (anywhere IPv4)

After setting up the environment you can run the scripts as guided below.


# Image_Server.py
The main node (master) running which has a Flask web server to receive the user photo uploads. (up to 50 tested on t3.micro free tier, 3 machines (1 master + 2 slaves))
To run this script it needs to have the templates folder ( in the same directory containing the index.html + processing.html files).

