#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：PlottingFigures 
@File    ：close.py
@IDE     ：PyCharm 
@Author  ：Zihan Ding
@Date    ：3/31/23 9:53 PM 
@Description:
'''

import psutil

# get all open file descriptors for this process
process = psutil.Process()
fds = process.open_files()

# close all open files
for fd in fds:
    fd.close()
