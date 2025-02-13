## **User friendly Drone Control using LLM for Real World Applications**
* **Video Link:** https://drive.google.com/file/d/1dOKmB3zOpzwdu78Gn23d-EAwSZEXjSmE/view?usp=sharing

**Installtion:**

System requirement:

*  Ubuntu 20.04
*  ROS: Noetic
*  Python 3.6
*  Gazebo
*  Ardupilot plugin for drone simulation
*  Qground control for arming drones and sending commands to drones
*  Mavros package for drone ros communication 

```
pip install rospy
pip install pyqt5
pip install geometry_msgs
pip install nav_msgs
pip install tf
pip install guidance
```



How to execute? (works for both simualtion and real world drones)

#drone ros communciation
```
roslaunch mavros apm.launch

#this is for ui and drone control
python ui.py 
