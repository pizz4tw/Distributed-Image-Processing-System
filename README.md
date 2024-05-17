# Distributed-Image-Processing-System
A distributed image processing system that runs on a cluster of computers on the cloud using AWS EC2 services.

# Setting up the Cloud environment
This system assumes you already set-up an EC2 Cluster environment between master and slave nodes, if you don't know how you can refer to this link: 
https://blog.glennklockwood.com/2013/04/quick-mpi-cluster-setup-on-amazon-ec2.html

Make sure you modify the security groups to allow for HTTP requests on port 5000 from 0.0.0.0 (anywhere IPv4) also setup the /shared folder between the 3 machines using these commands:

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
Now you should have a shared folder between the machines that they can communicate on and distribute the tasks between them.
After setting up the environment you can run the scripts as guided below.


# Image_Server.py
The main node (master) running which has a Flask web server to receive the user photo uploads. (up to 50 tested on t3.micro free tier, 3 machines (1 master + 2 slaves))
To run this script it needs to have the templates folder ( in the same directory containing the index.html + processing.html files.)
After the server is run the user can input the IPaddress:PORT (which in our case IPaddressOfMaster:5000) then they are greeted with a 

