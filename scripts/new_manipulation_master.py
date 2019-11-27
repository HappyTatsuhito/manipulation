#!/usr/bin/env python
# -*- coding: utf-8 -*

import rospy
import actionlib
# ros msgs
from std_msgs.msg import String
from geometry_msgs.msg import Twist
# ros srvs
from manipulation.srv import ManipulateSrv
# action msgs
from manipulation.msg import *

arm_change_pub = rospy.Publisher('/arm/changing_pose_req',String,queue_size=1)


class ObjectRecognizer(object):
    def __init__(self):
        self.feedback_flg = None

    def recognizerFeedback(self,msg):
        rospy.loginfo('feedback : %s'%(msg))
        self.feedback_flg = msg.recog_feedback
        
    def recognizeObject(self,target_name):
        act = actionlib.SimpleActionClient('/object/localize', ObjectRecognizerAction)
        rospy.loginfo('Start action with Recognizer')
        act.wait_for_server(rospy.Duration(5))
        goal = ObjectRecognizerGoal()
        goal.recog_goal = target_name
        act.send_goal(goal, feedback_cb = self.recognizerFeedback)
        loop_count = 0
        result = None
        while result == None and not rospy.is_shutdown():
            result = act.get_result()
            if self.feedback_flg:
                loop_count = 0
                self.feedback_flg = None
            elif self.feedback_flg == False:# Noneで入ってしまう(;_;)
                loop_count += 1
                self.feedback_flg = None
            if loop_count > 9:
                act.cancel_goal()
            rospy.Rate(3.0).sleep()
        result = act.get_result()
        recognize_flg = loop_count < 10

        return recognize_flg, result.recog_result

class ObjectGrasper(object):
    def __init__(self):
        pass

    def grasperFeedback(self,msg):
        rospy.loginfo('feedback %s'%(msg))

    def graspObject(self, target_centroid):
        act = actionlib.SimpleActionClient('/object/grasp', ObjectGrasperAction)
        rospy.loginfo('waiting for grasper server')
        act.wait_for_server(rospy.Duration(5))
        rospy.loginfo('send goal')
        goal = ObjectGrasperGoal()
        goal.grasp_goal = target_centroid
        act.send_goal(goal, feedback_cb = self.grasperFeedback)
        act.wait_for_result()
        result = act.get_result()

        return result.grasp_result

def main(req):
    rospy.sleep(1.0)
    pose_req = String()
    pose_req.data = 'carry'
    global arm_change_pub
    arm_change_pub.publish(pose_req)
    recognize_flg = True
    grasp_flg = False
    grasp_count = 0
    OR = ObjectRecognizer()
    OG = ObjectGrasper()
    while recognize_flg and not grasp_flg and grasp_count < 6 and not rospy.is_shutdown():
        rospy.loginfo('----- Recognizer -----')
        recognize_flg, object_centroid = OR.recognizeObject(req.target)
        if recognize_flg:
            rospy.loginfo('-----  Grasper   -----')
            grasp_flg = OG.graspObject(object_centroid)
            grasp_count += 1
    manipulation_flg = recognize_flg and grasp_flg
        
    return manipulation_flg

    
if __name__ == '__main__':
    rospy.init_node('manipulation_master')
    #ros_service
    manipulation = rospy.Service('/manipulation',ManipulateSrv, main)
    rospy.spin()
