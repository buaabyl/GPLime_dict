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
import nltk
import copy
import pickle

def file_put_cache(fn, d):
    f = open(fn, 'wb')
    pickle.dump(d, f)
    f.close()

def file_get_cache(fn):
    f = open(fn, 'rb')
    d = pickle.load(f)
    f.close()
    return d

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

def word2pinyin(word, pinyin_map, log):
    if word in pinyin_map:
        return pinyin_map[word][0]

    log.write('Try to find pinyin for: %s: ' % word)

    # greedy longest match for pinyin
    skip = False
    words = copy.deepcopy(word)
    l = []
    while len(words) > 0:
        current_len = len(words)
        n = len(words)
        while n > 0:
            subk = words[:n]
            if subk in pinyin_map:
                candidate = pinyin_map[subk]
                if n > 1:
                    l.extend(candidate[0].split(','))
                else:
                    l.append(candidate[0])
                words = words[n:]
            else:
                n = n - 1

        if current_len == len(words):
            skip = True
            break

    if len(l) != len(k):
        skip = True

    if skip:
        log.write(' fail!\n')
        return None

    pinyin = ','.join(l)
    log.write(' found! %s\n' % str(pinyin))

    return pinyin

if __name__ == '__main__':
    PINYIN_MAP_CACHE        = '../WORDS2PINYINS.cache'
    JIEBA_CHINESE_DATAFILE  = '../jieba.dict'
    NGRAM_ORIGINAL_DB       = ['unigram.cache', 'bigram.cache']
    NGRAM_MERGED_DB         = 'ngram_chs.db'

    if not os.path.isfile(PINYIN_MAP_CACHE):
        print('missing:', PINYIN_MAP_CACHE)
        sys.exit(-1)
    print('loading:', PINYIN_MAP_CACHE)
    pinyin_map = file_get_cache(PINYIN_MAP_CACHE)


    if not os.path.isfile(JIEBA_CHINESE_DATAFILE):
        print('Missing', JIEBA_CHINESE_DATAFILE)
        sys.exit(-1)
    for fn in NGRAM_ORIGINAL_DB:
        if not os.path.isfile(fn):
            print('Missing', fn)
            sys.exit(-1)

    words_list = load_jieba_user_dict(JIEBA_CHINESE_DATAFILE)
    print('loaded jieba words list', len(words_list), 'words')

    dbname = NGRAM_MERGED_DB
    print('target db name:', dbname) 
    if os.path.exists(dbname):
        os.remove(dbname)

    db = sqlite3.connect(dbname)
    cur = db.cursor()
    cur.execute('CREATE TABLE unigram(phrase TEXT, freq REAL, pinyin TEXT)')
    cur.execute('CREATE TABLE unigram_count(value INTEGER)')
    cur.execute('CREATE TABLE bigram(phrase0 TEXT, phrase1 TEXT, logp REAL)')


    # --------------------------------------------------------------------------
    unigram = file_get_cache('unigram.cache')

    total_unigram = 0
    for key, cnt in unigram.items():
        total_unigram = total_unigram + cnt
    for word in words_list:
        if word not in unigram:
            unigram[word] = 0

    # every record add one
    total_unigram += len(unigram)

    del words_list
    gc.collect(2)

    print('open pinyin_matching.log')
    log = open('pinyin_matching.log', 'w', encoding='UTF-8')

    print('insert unigram into sqlite3 db')
    print(' unigram =', total_unigram)
    max_freqcnt = None
    min_freqcnt = None
    for k, v in unigram.items():
        # just counter
        freqcnt = v + 1
        if min_freqcnt == None:
            min_freqcnt = freqcnt
            max_freqcnt = freqcnt
        if freqcnt > max_freqcnt:
            max_freqcnt = freqcnt
        if freqcnt < min_freqcnt:
            min_freqcnt = freqcnt

        pinyin = word2pinyin(k, pinyin_map, log)
        if pinyin:
            cur.execute('INSERT INTO unigram(phrase, freq, pinyin) VALUES(?, ?, ?)', (k, freqcnt, pinyin))

    cur.execute('INSERT INTO unigram_count(value) VALUES(?)', [max_freqcnt])
    print('freqcnt range:', min_freqcnt, max_freqcnt)

    res = cur.execute('SELECT phrase0, phrase1, logp from bigram ORDER BY logp ASC LIMIT 20', [max_freqcnt])
    if res:
        rows = res.fetchall()
        for phrase0, phrase1, logp in rows:
            print('%.8f, %.20s, %.20s' % (logp, phrase0, phrase1))

    log.close()


    # --------------------------------------------------------------------------
    bigram  = file_get_cache('bigram.cache')
    print('insert bigram into sqlite3 db')
    max_p = None
    min_p = None
    for k, v in bigram.items():
        k1, k2 = k.split(' ')
        bi_freq = v
        uni_freq = unigram[k1] + 1

        if uni_freq == 0 or bi_freq == 0:
            print('IGNORE', k1, k2, bi_freq, uni_freq)
            continue

        logp= -math.log(bi_freq/uni_freq)
        if min_p == None:
            min_p = logp
            max_p = logp
        if logp > max_p:
            max_p = logp
        if logp < min_p:
            min_p = logp
        cur.execute('INSERT INTO bigram(phrase0, phrase1, logp) VALUES(?, ?, ?)', (k1, k2, logp))

    del unigram
    gc.collect(2)

    del bigram
    gc.collect(2)
    print('entropy range:', min_p, max_p)


    db.commit()


    print('create index')
    cur.execute('CREATE INDEX index_bigram ON bigram(phrase0, phrase1)')
    db.commit()

    

