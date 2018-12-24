#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint
from std_msgs.msg import Int32
from scipy.spatial import KDTree
import numpy as np

import math

'''
This node will publish waypoints from the car's current position to some `x` distance ahead.

As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.

Once you have created dbw_node, you will update this node to use the status of traffic lights too.

Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.

TODO (for Yousuf and Aaron): Stopline location for each traffic light.
'''

class WaypointUpdater(object):
    def __init__(self):
        rospy.init_node('waypoint_updater')

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)
        rospy.Subscriber('/traffic_waypoint', Int32, self.traffic_cb)
        #rospy.Subscriber('/obstacle_waypoint', Lane, self.obstacle_cb)

        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)

        self.lookahead_wps = rospy.get_param('~lookahead_wps', 40)
        self.waypoint_update_frequency = rospy.get_param('~waypoint_update_frequency', 50)
        self.traffic_light_stop_distance = rospy.get_param('~traffic_light_stop_distance', 15)
        self.traffic_light_lookahead_wps = rospy.get_param('~traffic_light_lookahead_wps', 100)
        self.max_deceleration = rospy.get_param('~max_deceleration', 1.0)

        self.pose = None
        self.waypoints = None
        self.waypoints_header = None
        self.waypoints_2d = None
        self.waypoints_kd = None
        self.waypoints_dist = None
        self.traffic_light_idx = None
        self.last_traffic = -1

        self.loop()
        
    def loop(self):
        rate = rospy.Rate(self.waypoint_update_frequency)
        while not rospy.is_shutdown():
            if self.pose and self.waypoints_kd:
                closest_waypoint_idx = self.find_closest_waypoint([self.pose.position.x, self.pose.position.y])
                self.publish_waypoints(closest_waypoint_idx, self.lookahead_wps)
            rate.sleep()
    
    def normalize_index(self, idx):
        return idx % len(self.waypoints_2d)

    def find_closest_waypoint(self, pos):
        idx = self.waypoints_kd.query(pos, 1)[1]
        closest_pos = np.array(self.waypoints_2d[idx])
        prev_pos = np.array(self.waypoints_2d[idx - 1])
        v_way = closest_pos - prev_pos
        v_pos = np.array(pos) - closest_pos
        if np.dot(v_way, v_pos) > 0:
            idx = self.normalize_index(idx + 1)
        rospy.loginfo("Closest wp: %d, (%f,%f)->(%f,%f)",idx, pos[0], pos[1], self.waypoints_2d[idx][0], self.waypoints_2d[idx][1])
        return idx
    
    def publish_waypoints(self, idx, pts):
        lane = self.generate_lane(idx, pts)
        self.final_waypoints_pub.publish(lane)
        
    def generate_lane(self, idx, pts):
        lane = Lane()
        lane.header = self.waypoints_header
        if self.traffic_light_idx and idx + 2 < self.traffic_light_idx < idx + self.traffic_light_lookahead_wps:
            lane.waypoints = self.decelerate_waypoints(idx, pts)
        else:
            lane.waypoints = self.waypoints[idx:idx+pts]
        return lane
    
    def decelerate_waypoints(self, idx, pts):
        waypoints = []
        for i in range(idx, idx + pts + 1):
            wp = self.waypoints[i]
            p = Waypoint()
            p.pose = wp.pose
            dist = self.distance(i, self.traffic_light_idx) - self.traffic_light_stop_distance
            v = math.sqrt(2.0 * self.max_deceleration * dist) if dist > 0 else 0
            p.twist.twist.linear.x = min(v if v >= 1 else 0, wp.twist.twist.linear.x)
            waypoints.append(p)
            rospy.loginfo("%s -> %s, distance: %f, velocity: %f", i, self.traffic_light_idx, dist, v)
        return waypoints
        
    def pose_cb(self, msg):
        self.pose = msg.pose
        rospy.loginfo("Pose: (%s,%s)", self.pose.position.x, self.pose.position.y)

    def waypoints_cb(self, waypoints):
        self.waypoints  = waypoints.waypoints
        self.waypoints_header = waypoints.header
        if self.waypoints_2d is None:
            rospy.loginfo("Initialize waypoints ...")
            self.waypoints_2d = [[waypoint.pose.pose.position.x, waypoint.pose.pose.position.y] for waypoint in self.waypoints]
            self.waypoints_kd = KDTree(self.waypoints_2d)
            dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
            self.waypoints_dist = [dl(self.waypoints[i-1].pose.pose.position, self.waypoints[i].pose.pose.position) if i > 0 else 0 for i in range(0, len(self.waypoints))]
            for i in range(2, len(self.waypoints)):
                self.waypoints_dist[i] += self.waypoints_dist[i-1]
            rospy.loginfo("Initialized waypoints %s", self.waypoints_kd)
 #           for i in range(0, len(self.waypoints)):
 #               rospy.loginfo("(%f,%f,%f,%f, %f", self.waypoints[i].pose.pose.position.x, self.waypoints[i].pose.pose.position.y, self.waypoints[i].twist.twist.linear.x, self.waypoints[i].twist.twist.angular.z, self.waypoints_dist[i])
            
    def traffic_cb(self, msg):
        self.traffic_light_idx = msg.data
        rospy.logdebug("Traffic light: %s", self.traffic_light_idx)

    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, wp1, wp2):
        return self.waypoints_dist[wp2] - self.waypoints_dist[wp1]

if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
