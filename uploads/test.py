#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# email: freewayrong@foxmail.com
# github: https://github.com/hiddenblue
# author: Chase xia

from subprocess import Popen, PIPE
import zhconv

# cmd = ['ls']
cmd = ['/home/chase/Documents/miniconda3/envs/whisper/bin/python', '/home/chase/Documents/miniconda3/envs/whisper/bin/whisper', '/home/chase/Downloads/en.flac', '--model', 'medium', '--language', 'Chinese']

proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
stdout, stderr = proc.communicate()
stdout = zhconv.convert(stdout.decode("utf-8"), 'zh-cn')

print(stdout, "\n", stderr)