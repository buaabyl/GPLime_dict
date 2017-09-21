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
# @ref https://stanfordnlp.github.io/CoreNLP/
#
# TODO: choose more effective database, sqlite3 is not suitable,
# leveldb is too complex...
#
# @author william bao
# 0.0.1 unigram and bigram model for testing
#
#
import sys
import os
import re
import getopt
import glob
import json
import math
import sqlite3
import time

def file_put_json(dbname, d):
    jstr = json.dumps(d, indent=4)
    f = open(dbname, 'w', encoding='utf-8')
    f.write(jstr)
    f.close()

def file_get_json(dbname):
    f = open(dbname, 'r', encoding='utf-8')
    jstr = f.read()
    f.close()
    db = json.loads(jstr)
    return db

if __name__ == '__main__':
    dbname = 'ngram_chs.db'
    db = sqlite3.connect(dbname)
    cur = db.cursor()


    s = '这 是 一个 简单的 测试 用例'
    tokens = s.split(' ')

    i = 0
    n = len(tokens)
    l = []
    while i < n:
        token = tokens[i]
        l.append(token)
        print('INPUT:', ' '.join(l), '[  ]')

        t1 = time.time()
        res = cur.execute('SELECT freq FROM unigram')
        t2 = time.time()
        if res:
            freq = res.fetchone()[0]
            res = cur.execute('SELECT phrase1, freq FROM bigram WHERE phrase0 = ? ORDER BY freq ASC LIMIT 20', [token])
            t3 = time.time()
            if res:
                for row in res.fetchall():
                    print('', row)

        print('* unigram', t2-t1, 'seconds')
        print('* bigram', t3-t2, 'seconds')

        i = i + 1
        print()




