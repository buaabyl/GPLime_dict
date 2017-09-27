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
import sys
import os
import re
import getopt
import glob
import math
import json
import sqlite3

if __name__ == '__main__':
    db = sqlite3.connect('ngram_chs.db')
    cur = db.cursor()

    m = {}

    #res = cur.execute('SELECT pinyin, freq FROM unigram LIMIT 1000')
    res = cur.execute('SELECT pinyin, freq FROM unigram')
    if res:
        rows = res.fetchall()
        n = len(rows)
        i = 0
        for row in rows:
            i = i + 1
            sys.stdout.write('%6.2f%% (%d/%d)\r' % (100 * i / n, i, n))
            pinyins = row[0].split(',')
            freq    = row[1]
            for pinyin in pinyins:
                if pinyin not in m:
                    m[pinyin] = freq
                else:
                    m[pinyin] = m[pinyin] + freq
    
    total = 0
    for pinyin, freq in m.items():
        total = total + freq

    model = {}
    for pinyin, freq in m.items():
        p = freq / total
        entropy = - p * math.log(p)
        model[pinyin] = entropy

    f = open('pinyin.unigram', 'w')
    l = [(k, v) for k,v in model.items()]
    l.sort(key=lambda v:v[1], reverse=True)

    msg = []
    for k, v in l:
        msg.append('    %-10s: %.8f' % ('"%s"' % k, v))


    f.write('{\n')
    f.write(',\n'.join(msg))
    f.write('\n}\n')
    #jstr = json.dumps(model, indent=4)
    #f.write(jstr)
    f.close()


