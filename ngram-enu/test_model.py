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
    dbname = 'ngram_enu.db'
    db = sqlite3.connect(dbname)
    cur = db.cursor()


    s = 'i am interested in learning english'
    tokens = s.split(' ')

    i = 0
    n = len(tokens)
    l = []
    while i < n:
        token = tokens[i]
        l.append(token)
        print('INPUT:', ' '.join(l), '[  ]')

        res = cur.execute('SELECT freq FROM unigram')
        if res:
            freq = res.fetchone()[0]
            res = cur.execute('SELECT phrase1, freq FROM bigram WHERE phrase0 = ? ORDER BY freq ASC LIMIT 20', [token])
            if res:
                for row in res.fetchall():
                    print('', row)

        i = i + 1
        print()




