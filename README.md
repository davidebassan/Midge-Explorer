# Explorer

***Thesis***


## Requirements
***
### **Ros 1**
```
 View installation guide at https://www.ros.org/install/
```
### **Xacro**
```
 sudo apt-get install ros-<version>-xacro  
```
### **Gazebo**
```
 sudo apt-get install ros-<version>-gazebo  
```

### **RosBridge and Tf2 Web Republisher**
```
 sudo apt-get install ros-<version>-rosbridge-suite
 sudo apt-get install ros-<version>-tf2-web-republisher  
```

### **MoveBase**
```
 sudo apt-get install ros-<version>-move-base  
```

### **Joy**
```
 sudo apt-get install ros-<version>-joy  
```

## Installation
***
```
 git clone https://github.com/davidebassan/Explorer # Clone
```
```
 cd midge_ws 
```
```
 catkin_make # build the package 
```
```
 source devel/setup.bash 
```
```
 roslaunch midge world.launch 
```
```
rosrun midge midge.py
```
