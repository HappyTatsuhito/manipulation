#!/usr/bin/env python
# -*- coding: utf-8 -*

import rospy
import actionlib
from std_srvs.srv import SetBool
from geometry_msgs.msg import Twist
from manipulation.msg import *

class ObjectRecognizer(object):
    def __init__(self):
        self.feedback_flg = 'None'

    def recognizerFeedback(self,msg):
        rospy.loginfo('feedback %s'%(msg))
        self.feedback_flg = msg.recog_feedback
        
    def recognizeObject(self,target_name):
        ac = actionlib.SimpleActionClient('/object/localize', ObjectRecognizerAction)
        rospy.loginfo('waiting for recognizer server')
        ac.wait_for_server(rospy.Duration(5))
        rospy.loginfo('send goal')
        goal = ObjectRecognizerGoal()
        goal.recog_goal = target_name
        ac.send_goal(goal, feedback_cb = self.recognizerFeedback)
        loop_count = 0
        rate = rospy.Rate
        while not ac.wait_for_result() and not rospy.is_shutdown():
            rospy.loginfo(loop_count)
            if self.feedback_flg:
                loop_count = 0
                self.feedback_flg = 'None'
            else:
                loop_count += 1
                self.feedback_flg = 'None'
            if loop_count > 9:
                ac.cancel_goal()
            rospy.Rate().sleep(3.0)
        result = ac.get_result()
        recognize_flg = loop_count < 10

        return recognize_flg, result.recog_result

class ObjectGrasper(object):
    def __init__(self):
        pass

    def grasperFeedback(self,msg):
        rospy.loginfo('feedback %s'%(msg))

    def graspObject(self, target_centroid):
        ac = actionlib.SimpleActionClient('/object/grasp', ObjectGrasperAction)
        rospy.loginfo('waiting for grasper server')
        ac.wait_for_server(rospy.Duration(5))
        rospy.loginfo('send goal')
        goal = ObjectGrasperGoal()
        goal.recog_goal = target_centroid
        ac.send_goal(goal, feedback_cb = self.grasperFeedback)
        ac.wait_for_result()
        result = ac.get_result()

        return result

def main(req):
    recognize_flg = False
    grasp_flg = False
    OR = ObjectRecognizer()
    recognize_flg, object_centroid = OR.recognizeObject('cup')
    if recognize_flg:
        OG = ObjectGrasper()
        #grasp_flg = OG.graspObject(object_centroid)
    manipulation_flg = recognize_flg and grasp_flg
    finish_message = 'finish'
        
    return manipulation_flg, finish_message

    
if __name__ == '__main__':
    rospy.init_node('manipulation_master')
    #ros_service
    manipulation = rospy.Service('/manipulation', SetBool, main)
    rospy.spin()
