# Programming A Real Self-Driving Car

## By Team Autonomous Mobility

### Team Lead: Tony Lin

### Members:

|        Name         |            Email             |
|---------------------|:-----------------------------|
|     James Korge	  |       jk5128@nyu.edu         |
|     Yulong Li	      |      hiyulongl@gmail.com	 |
|    Islam Sherif     |   eng.islam.sherif@gmail.com |
|   Fuqiang Huang	  |       fuqiang@wustl.edu      |
|     Tony Lin        |     dr.tony.lin@gmail.com	 |

## Credits

* The training data for traffic light detector was from https://github.com/alex-lechner/Traffic-Light-Classification
* For the simulator, the traffic light classifier uses SSD Mobilenet implementation from https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md,
commit dc78c085 for Tensorflow 1.3 compatibility
* For the site, the traffic light classifier uses SSD inception V2 pre-trained model from https://github.com/alex-lechner/Traffic-Light-Classification

## Usage

### Run the simulator testing

1. Run the followings

```bash
cd ros
catkin_make
source devel/setup.sh
roslaunch launch/styx.launch
```

2. Launch the simulator, check <B>Camera</B> and uncheck <B>Manual</B>

### Real world testing

1. Download [training bag](https://s3-us-west-1.amazonaws.com/udacity-selfdrivingcar/traffic_light_bag_file.zip) that was recorded on the Udacity self-driving car.

2. Unzip the file

```bash
unzip traffic_light_bag_file.zip
```

3. Play the bag file

```bash
rosbag play -l traffic_light_bag_file/traffic_light_training.bag
```

4. Launch your project in site mode

```bash
cd CarND-Capstone/ros
roslaunch launch/site.launch
```

5. Confirm that traffic light detection works on real life images

## Configuration Parameters

### Global Parameters

The following global parameters are provided under ros/launch/styx.launch, and ros/launch/site.launch:

* loglevel: we use this parameter to control logging on top of ros's logging framework
* traffic_light_classifier_model: the trained model for traffic light detection

#### Waypoint Update

Waypoint updater takes the following parameters:

* lookahead_wps: the number of waypoints to updates in every cycle
* waypoint_update_frequency: the waypoint update frequency
* traffic_light_stop_distance: the stop distance for traffic light
* traffic_light_lookahead_wps: the number of waypoints that we need to decelerate for red light
* max_deceleration: maximum deceleration to stop for traffic light

#### Waypoint Follower

Waypoint follower's pure pursuit algorithm takes the following parameters:

* publish_frequency: the frequency for publishing twist
* subscriber_queue_length: the subscriber queue length for final_waypoints, current_pose, and current_velocity topics
* const_lookahead_distance: pure pursuit constant lookahead distance
* minimum_lookahead_distance: pure pursuit maximum lookahead distance
* lookahead_distance_ratio: pure pursuit lookahead distance ratio with respect to velocity
* maximum_lookahead_distance_ratio: pure pursuit maximum lookahead distance ratio with respect to velocity

#### Twist Controller

The twist controller takes the following parameters:

control_update_frequency: the frequency that the controller should publish throttle, steering, and brake

#### Vehicle Parameters

The twist controller uses the following parameters for the vehicle:

* vehicle_mass: mass of the vehicle
* fuel_capacity: fuel capacity
* brake_deadband: brake deadband
* decel_limit: deceleration limit
* accel_limit: acceleration limit
* wheel_radius: wheel radius
* wheel_base: wheel base length
* steer_ratio: steering ratio
* max_lat_accel: maximum lateral acceleration
* max_throttle: maximum throttle
* max_steer_angle: maximum steering angle
* full_stop_brake_keep: the amount of brake to keep when the stopping the vehicle
* full_stop_brake_limit: the maximum amount of brake that could be applied to the vehicle
* brake_deceleration_start: to avoid braking the vehicle too frequently, this parameter provides the threshold on when brake should be applied

#### Traffic Light Detecter

The traffic light detector use the global parameter, traffic_light_classifier_model, to refer to the Tensorflow classification model.
In addition, the following parameters are used for the classification:

* min_positive_score: the minimal score for the result to be considered positive

## Traffic Light Detection Package

### For the Simulator

SSD Mobilenet V1 is used for detection and classification. It is re-trained from https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md,
commit dc78c085 for Tensorflow 1.3 compatibility.

### For the Site

The traffic light detection and classification uses a SSD Inception V2 pre-trained model from https://github.com/alex-lechner/Traffic-Light-Classification. It is based on commit f7e99c0 of https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md for Tensowflow 1.4 compatibility. It also works for Tendowflow 1.3.

## Waypoint Updater Package


## BDW Package


## Waypoint Follower Package


## Waypoint Util Package


### Diagnostic Tool
1. Make sure that the python dependencies installed before using the diagnosis tool
```
pip install -r requirements_debug.txt
```

2. Open a new terminal and source
```bash
cd ~/CarND-Capstone
cd ros
source devel/setup.bash
```

3. Make the diagnosis python file executable
```bash
cd src/tools
chmod +x diagScreen.py
cd ~/CarND-Capstone/ros
```

4. Run the diagnosis file
```bash
rosrun tools diagScreen.py --screensize 5 --maxhistory 800 --textspacing 75 --fontsize 1.5
```
Note that there are five options to choose the screensize:  
help='Screen sizes: 1:2500x2500px, 2:1250x1250px, 3:833x833px, 4:625x625px, 5:500x500px '   
You can choose anyone that you like.

## Issues

We had lots of issues with the simulator, from times, the simulator will either stop sending pose and velocity updates, and send invalid pose and velocity (mostly 0 velocity) updates.
We have tried to accommodated missing updates in the Waypoint Updater by estimating the possible velocity and pose when we detect missing updates.

However, bogus updates cannot be detected easily as there is no other basis for detecting whether an update from the simulator is valid or not.

We have eaised the issue in the student hub, but did not have any feedbacks on this.

## Discussion

The baseline project uses the Pure Pursuit algorithm for controling the lateral and angular velocity of the vehicle, and PID for determining the throttle.
It would be interesting to compare this with MPC.
