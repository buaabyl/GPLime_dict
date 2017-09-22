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

def write_unigram_bigram_to_sqlite3(dbname, unigram, bigram):
    print('db:', dbname) 
    if os.path.exists(dbname):
        os.remove(dbname)
    total_unigram = 0
    total_bigram  = 0
    for key, cnt in unigram:
        total_unigram = total_unigram + cnt
    for first, second, cnt in bigram:
        total_bigram = total_bigram + cnt
    print('total count:')
    print(' unigram =', total_unigram)
    print(' bigram  =', total_bigram)

    db = sqlite3.connect(dbname)
    cur = db.cursor()
    cur.execute('CREATE TABLE unigram(phrase TEXT, logp REAL)')
    cur.execute('CREATE TABLE bigram(phrase0 TEXT, phrase1 TEXT, logp REAL)')

    print('insert unigram into sqlite3 db')
    for k, v in unigram:
        logp = -math.log(v/total_unigram)
        cur.execute('INSERT INTO unigram(phrase, logp) VALUES(?, ?)', (k, logp))

    print('insert bigram into sqlite3 db')
    for k1, k2, v in bigram:
        logp = -math.log(v/total_bigram)
        cur.execute('INSERT INTO bigram(phrase0, phrase1, logp) VALUES(?, ?, ?)', (k1, k2, logp))

    db.commit()

    print('create index')
    cur.execute('CREATE INDEX index_bigram ON bigram(phrase0, phrase1)')
    db.commit()

def load_google_english_list(fn):
    f = open(fn, 'r')
    d = f.read()
    f.close()
    
    l = []
    lines = d.splitlines()
    pattern = re.compile(r'^\W+|\W+$')
    for line in lines:
        if len(line) == 0:
            continue
        # remove prefix and suffix space
        k = pattern.sub('', line)
        n = len(k)
        if n == 0:
            continue

        l.append(k)

    return l

if __name__ == '__main__':
    GOOGLE_ENGLISH_DATAFILE = 'google_english.txt'
    NGRAM_ORIGINAL_DB       = ['unigram.json', 'bigram.json']
    NGRAM_MERGED_DB         = 'ngram_enu.db'
    if not os.path.isfile(GOOGLE_ENGLISH_DATAFILE):
        print('Missing', GOOGLE_ENGLISH_DATAFILE)
        sys.exit(-1)
    for fn in NGRAM_ORIGINAL_DB:
        if not os.path.isfile(fn):
            print('Missing', fn)
            sys.exit(-1)

    total_unigram = 0
    total_bigram  = 0
    unigram = file_get_json('unigram.json')
    bigram  = file_get_json('bigram.json')

    for key, cnt in unigram:
        total_unigram = total_unigram + cnt
    for first, second, cnt in bigram:
        total_bigram = total_bigram + cnt
    print('total count:')
    print(' unigram =', total_unigram)
    print(' bigram  =', total_bigram)

    google_words_list = load_google_english_list(GOOGLE_ENGLISH_DATAFILE)
    print('loaded google words list', len(google_words_list))

    # We need to do some research on it, but just add one for testing
    for kv in unigram:
        kv[1] = kv[1] + 1
    for word in google_words_list:
        unigram.append([word, 1])
    
    write_unigram_bigram_to_sqlite3(NGRAM_MERGED_DB, unigram, bigram)
    





