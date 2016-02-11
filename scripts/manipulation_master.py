#!/usr/bin/env python
# -*- coding: utf-8 -*

import rospy
from std_msgs.msg import String,Bool
from geometry_msgs.msg import Twist

class ManipulationMaster(object):
    def __init__(self):
        grasp_sub = rospy.Subscriber('/object/grasp_req',String,self.main)
        localize_sub = rospy.Subscriber('/object/localize/res',Bool,self.localizeResultCB)
        manipulate_sub = rospy.Subscriber('/object/manipulate/res',Bool,self.manipulateResultCB)
        manipulate_retry_sub = rospy.Subscriber('/object/manipulate/retry',String,self.retryRequestCB)
        self.localize_req_pub = rospy.Publisher('/object/localize/req',String,queue_size=1)
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

    def retryRequestCB(self,res):
        self.manipulate_result_flg = res.data
        return

    # object_grasperと一緒
    # common_pkgに作ろう
    def moveBase(self,rad_speed):
        cmd = Twist()
        for speed_i in range(10):
            cmd.linear.x = rad_speed*0.05*speed_i
            cmd.angular.z = 0
            self.cmd_vel_pub.publish(cmd)
            rospy.sleep(0.1)
        for speed_i in range(10):
            cmd.linear.x = rad_speed*0.05*(10-speed_i)
            cmd.angular.z = 0
            self.cmd_vel_pub.publish(cmd)
            rospy.sleep(0.1)
        cmd.linear.x = 0
        cmd.angular.z = 0
        self.cmd_vel_pub.publish(cmd)
        return
                
    def main(self,req):
        cmd = Twist()
        cmd.linear.x = 0
        rate = rospy.Rate(5.0)
        loop_count = 0
        #for m in range(3):
        while loop_count < 3:
            self.manipulate_result_flg = 'None'
            for r in range(6):
                print 'Localize : ', r
                self.localize_result_flg = 'None'
                self.localize_req_pub.publish(req.data)
                rospy.sleep(1.0)
                while self.localize_result_flg == 'None' and not rospy.is_shutdown():
                    rate.sleep()
                if self.localize_result_flg:
                    break
                else:
                    cmd.angular.z = -2*(((r+1)%4)/2) + 1.0
                    self.cmd_vel_pub.publish(cmd)
            if not self.localize_result_flg:
                self.manipulate_result_flg = False
                break
            print 'Manipulate : ', loop_count
            while self.manipulate_result_flg == 'None' and not rospy.is_shutdown():
                rate.sleep()
            if self.manipulate_result_flg == 'Retry':
                pass
            elif self.manipulate_result_flg and type(self.manipulate_result_flg) == Bool():
                break
            else:
                move_range = -1*(((loop_count+1)%4)/2)*1.2+0.6
                self.moveBase(move_range)
                loop_count += 1
        self.grasp_res_pub.publish(self.manipulate_result_flg)
        self.localize_result_flg = 'None'
        self.manipulate_result_flg = 'None'
        return

if __name__ == '__main__':
    rospy.init_node('manipulation_master')
    MM = ManipulationMaster()
    rospy.spin()
