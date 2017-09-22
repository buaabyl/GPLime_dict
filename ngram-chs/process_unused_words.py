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
#  2017.09.07      created by {user}
#
# @ref 斯坦福大学自然语言处理第五课-拼写纠错（spelling-correction）
# @url http://52opencourse.com/138/%E6%96%AF%E5%9D%A6%E7%A6%8F%E5%A4%A7%E5%AD%A6%E8%87%AA%E7%84%B6%E8%AF%AD%E8%A8%80%E5%A4%84%E7%90%86%E7%AC%AC%E4%BA%94%E8%AF%BE-%E6%8B%BC%E5%86%99%E7%BA%A0%E9%94%99%EF%BC%88spelling-correction%EF%BC%89
#
#
#
import sys
import os
import re
import getopt
import glob
import sqlite3
import json
import math
import gc

def file_put_json(fn, d):
    jstr = json.dumps(d, indent=4)
    f = open(fn, 'w', encoding='utf-8')
    f.write(jstr)
    f.close()

def file_get_json(dbname):
    f = open(dbname, 'r', encoding='utf-8')
    jstr = f.read()
    f.close()
    db = json.loads(jstr)
    return db

def load_jieba_user_dict(fn):
    f = open(fn, 'r', encoding='utf-8')
    d = f.read()
    f.close()
    
    l = []
    lines = d.splitlines()
    pattern = re.compile(r'\W+')
    for line in lines:
        if len(line) == 0:
            continue

        tokens = pattern.split(line)
        k = tokens[0]
        n = len(k)
        if n == 0:
            continue

        l.append(k)

    return l

if __name__ == '__main__':
    JIEBA_CHINESE_DATAFILE = '../jieba.dict'
    NGRAM_ORIGINAL_DB       = ['unigram.json', 'bigram.json']
    NGRAM_MERGED_DB         = 'ngram_full_chs.db'
    if not os.path.isfile(JIEBA_CHINESE_DATAFILE):
        print('Missing', JIEBA_CHINESE_DATAFILE)
        sys.exit(-1)
    for fn in NGRAM_ORIGINAL_DB:
        if not os.path.isfile(fn):
            print('Missing', fn)
            sys.exit(-1)

    dbname = NGRAM_MERGED_DB
    print('db:', dbname) 
    if os.path.exists(dbname):
        os.remove(dbname)

    db = sqlite3.connect(dbname)
    cur = db.cursor()
    cur.execute('CREATE TABLE unigram(phrase TEXT, freq REAL)')
    cur.execute('CREATE TABLE bigram(phrase0 TEXT, phrase1 TEXT, freq REAL)')


    words_list = load_jieba_user_dict(JIEBA_CHINESE_DATAFILE)
    print('loaded jieba words list', len(words_list))

    unigram = file_get_json('unigram.json')

    # We need to do some research on it, but just add one for testing
    for kv in unigram:
        kv[1] = kv[1] + 1
    for word in words_list:
        unigram.append([word, 1])
    del words_list
    gc.collect(2)

    total_unigram = 0
    for key, cnt in unigram:
        total_unigram = total_unigram + cnt
    print('insert unigram into sqlite3 db')
    print(' unigram =', total_unigram)
    max_entropy = None
    min_entropy = None
    for k, v in unigram:
        entropy = -math.log(v/total_unigram)
        if min_entropy == None:
            min_entropy = entropy
            max_entropy = entropy
        if entropy > max_entropy:
            max_entropy = entropy
        if entropy < min_entropy:
            min_entropy = entropy
        cur.execute('INSERT INTO unigram(phrase, freq) VALUES(?, ?)', (k, entropy))
    del unigram
    gc.collect(2)
    print('entropy range:', min_entropy, max_entropy)


    total_bigram  = 0
    bigram  = file_get_json('bigram.json')
    for first, second, cnt in bigram:
        total_bigram = total_bigram + cnt
    print('insert bigram into sqlite3 db')
    print(' bigram  =', total_bigram)
    max_entropy = None
    min_entropy = None
    for k1, k2, v in bigram:
        entropy = -math.log(v/total_bigram)
        if min_entropy == None:
            min_entropy = entropy
            max_entropy = entropy
        if entropy > max_entropy:
            max_entropy = entropy
        if entropy < min_entropy:
            min_entropy = entropy
        cur.execute('INSERT INTO bigram(phrase0, phrase1, freq) VALUES(?, ?, ?)', (k1, k2, entropy))
    del bigram
    gc.collect(2)
    print('entropy range:', min_entropy, max_entropy)


    db.commit()


    print('create index')
    cur.execute('CREATE INDEX index_bigram ON bigram(phrase0, phrase1)')
    db.commit()

    

