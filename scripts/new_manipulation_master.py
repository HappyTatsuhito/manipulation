#!/usr/bin/env python
# -*- coding: utf-8 -*

import rospy
import actionlib
from std_srvs.srv import SetBool

def main():
    manipulation = rospy.Service('/manipulation', SetBool, manipulationMaster)
    rospy.spin()

def manipulationMaster(req):
    grasp_flg = True
    error_message = 'Succeeded to grasp'
    return grasp_flg, error_message

if __name__ == '__main__':
    rospy.init_node('manipulation_master')
    main()
