#!/usr/bin/env python
# -*- coding: utf-8 -*

import rospy
from std_msgs.msg import String,Bool
from geometry_msgs.msg import Twist

class ManipulationMaster(object):
    def __init__(self):
        grasp_sub = rospy.Subscriber('/object/grasp_req',String,self.main)
        localize_sub = rospy.Subscriber('/object/localize_res',Bool,self.localizeResultCB)
        manipulate_sub = rospy.Subscriber('/object/manipulate_res',Bool,self.manipulateResultCB)
        self.localize_req_pub = rospy.Publisher('/object/localize_req',String,queue_size=1)
        self.grasp_res_pub = rospy.Publisher('/object/grasp_res',Bool,queue_size=1)
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel_mux/input/teleop',Twist,queue_size=1)

        self.localize_result_flg = 'None'
        self.manipulate_result_flg = 'None'
        
    def localizeResultCB(self,res):
        self.localize_result_flg = res.data
        return

    def manipulateResultCB(self,res):
        self.manipulate_result_flg = res.data
        return

    def main(self,req):
        cmd = Twist()
        cmd.linear.x = 0
        rate = rospy.Rate(5.0)
        for m in range(3):
            self.manipulate_result_flg = 'None'
            for r in range(6):
                print 'localize'
                self.localize_result_flg = 'None'
                self.localize_req_pub.publish(req.data)
                rospy.sleep(1.0)
                while self.localize_result_flg == 'None' and not rospy.is_shutdown():
                    rate.sleep()
                if self.localize_result_flg:
                    break
                else:
                    cmd.angular.z = -2*(((m+1)%4)/2) + 1.0
                    self.cmd_vel_pub.publish(cmd)
            if not self.localize_result_flg:
                self.manipulate_result_flg = False
                break
            print 'manipulate'
            while self.manipulate_result_flg == 'None' and not rospy.is_shutdown():
                rate.sleep()
            if self.manipulate_result_flg:
                break
        self.grasp_res_pub.publish(self.manipulate_result_flg)
        self.localize_result_flg = 'None'
        self.manipulate_result_flg = 'None'
        return

if __name__ == '__main__':
    rospy.init_node('manipulation_master')
    MM = ManipulationMaster()
    rospy.spin()
