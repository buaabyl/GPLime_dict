#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
#                   GNU GENERAL PUBLIC LICENSE
#                       Version 2, June 1991
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# 
#
import sys
import os
import re
import getopt
import glob
import jieba

if __name__ == '__main__':
    jieba.load_userdict('jieba.dict')

    s = "Since 1999, researchers with the Elephant Listening Project " + \
        "have used an acoustic monitoring system to record elephant sounds in the African rainforest. "
    seg_list = jieba.cut(s)
    for token in seg_list:
        print(repr(token))

