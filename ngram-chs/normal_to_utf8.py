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

if __name__ == '__main__':
    l = []
    for prefix, dirs, files in os.walk('.'):
        for fn in files:
            if os.path.splitext(fn)[1].lower() == '.txt':
                l.append(os.path.join(prefix, fn))

    for fn in l:
        try:
            try:
                f = open(fn, 'r', encoding='utf-8')
                d = f.read()
            except:
                f = open(fn, 'r', encoding='gbk')
                d = f.read()
        except:
            f.close()
            print('SKIP', fn)
            continue

        newfn = os.path.splitext(fn)[0] + '.utf-8'
        f = open(newfn, 'w', encoding='utf-8')
        f.write(d)
        f.close()

