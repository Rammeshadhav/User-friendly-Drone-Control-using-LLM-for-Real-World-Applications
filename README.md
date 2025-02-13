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
*  Please use you own Open AI API key to access the LLM model used in UI.py

```
pip install rospy
pip install pyqt5
pip install geometry_msgs
pip install nav_msgs
pip install tf
pip install guidance
```



How to execute? (works for both simualtion and real world drones)

* Drone ros communciation
```
roslaunch mavros apm.launch

#this is for ui and drone control
python ui.py 
```

**References:**
* OpenAI. (2024). ChatGPT (GPT 3.5) [Large language model]. https://chat.openai.com/chat
* Oborne, Michael (2019). Mission Planner (Version 1.3.70) [Computer software]. Retrieved from https://ardupilot.org/planner/
* Thomas, D., Woodall, W., & Fernandez, E. (2014). Next-generation ROS: Building on DDS. In ROSCon Chicago 2014. OpenRobotics. https://wiki.ros.org/noetic/Installation/Ubuntu

