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
# @author william bao
#
import sys
import os
import re
import gc
import getopt
import glob
import json
import sqlite3
import jieba
import math
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

def get_all_articles():
    l = []
    for prefix, dirs, files in os.walk('.'):
        for fn in files:
            if os.path.splitext(fn)[1] == '.utf-8':
                absfn = os.path.join(prefix, fn)
                f = open(absfn, 'r', encoding='utf-8')
                d = f.read()
                f.close()

                d = d.replace('\n', ' ')
                sentences = re.split(r'[，。！？：…（）【】—、‘’“”]', d)

                l.append((absfn, sentences))
    return l

def generate_plain_ngram():
    if os.path.isfile('unigram.cache') or os.path.isfile('bigram.cache'):
        return True

    CACHE = 'articles.cache'
    if os.path.isfile(CACHE):
        print('loading cache:', CACHE)
        list_of_articles = file_get_cache(CACHE)
    else:
        list_of_articles = get_all_articles()
        file_put_cache(CACHE, list_of_articles)

    BIG_DICT = '../jieba.dict'
    if os.path.isfile(BIG_DICT):
        print('loading BIG DICT:', BIG_DICT)
        print('this will cost 2-5 minutes at most when create `Prefix dict`!')
        jieba.load_userdict(BIG_DICT)

    unigram = {}
    bigram = {}
    N = len(list_of_articles)
    nr_processed = 0
    for _, lines in list_of_articles:
        msg = '%5.2f%% (%d/%d)\r' % (100 * nr_processed / N, nr_processed, N)
        sys.stdout.write(msg)
        nr_processed = nr_processed + 1

        for line in lines:
            previous = None
            res = jieba.cut(line)
            for token in res:
                # sikp white space
                if re.match(r'\W+', token):
                    previous = None
                    continue

                # skip english
                if re.match(r'[0-9a-zA-Z]+', token):
                    previous = None
                    continue

                if token not in unigram:
                    unigram[token] = 1
                else:
                    unigram[token] = unigram[token] + 1
                if previous:
                    k = previous + ' ' + str(token)
                    if k not in bigram:
                        bigram[k] = 1
                    else:
                        bigram[k] = bigram[k] + 1
                previous = str(token)

    gc.collect(2)

    print('\n')

    print('unigram', len(unigram))
    l = []
    for k,v in unigram.items():
        l.append((k, v))
    l = sorted(l, key=lambda v:v[1], reverse=True)
    del unigram
    gc.collect(2)
    file_put_cache('unigram.cache', l)
    #file_put_json('unigram.json', l)
    del l
    gc.collect(2)
    print('dump unigram')


    print('bigram', len(bigram))
    l = []
    for k,v in bigram.items():
        first, second = k.split(' ')
        l.append((first, second, v))
    l = sorted(l, key=lambda v:v[2], reverse=True)
    del bigram
    gc.collect(2)
    file_put_cache('bigram.cache', l)
    #file_put_json('bigram.json', l)
    del l
    gc.collect(2)
    print('dump bigram')


if __name__ == '__main__':
    PINYIN_MAP_CACHE = '../PINYIN_RLOOKUP.cache'
    if not os.path.isfile(PINYIN_MAP_CACHE):
        print('missing:', PINYIN_MAP_CACHE)
        sys.exit(-1)
    print('loading:', PINYIN_MAP_CACHE)
    pinyin_map = file_get_cache(PINYIN_MAP_CACHE)

    generate_plain_ngram()

    dbname = 'ngram_chs.db'
    print('write to', dbname) 
    if os.path.exists(dbname):
        os.remove(dbname)
    db = sqlite3.connect(dbname)
    cur = db.cursor()
    cur.execute('CREATE TABLE unigram(phrase TEXT, freq REAL, pinyin TEXT)')
    cur.execute('CREATE TABLE bigram(phrase0 TEXT, phrase1 TEXT, freq REAL)')

    print('open pinyin_matching.log')
    log = open('pinyin_matching.log', 'w', encoding='UTF-8')

    total_unigram = 0
    print('loading: unigram.cache')
    unigram = file_get_cache('unigram.cache')
    #unigram = file_get_json('unigram.json')
    for key, cnt in unigram:
        total_unigram = total_unigram + cnt
    print('insert unigram into sqlite3 db')
    print(' unigram =', total_unigram)
    for k, v in unigram:
        p = v / total_unigram
        entropy = - p * math.log(p)

        if k in pinyin_map:
            pinyin = pinyin_map[k][0]
        else:
            log.write('Try to find pinyin for: %s: ' % k)

            # greedy longest match for pinyin
            skip = False
            words = copy.deepcopy(k)
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
                continue

            pinyin = ','.join(l)
            log.write(' found! %s\n' % str(pinyin))

        cur.execute('INSERT INTO unigram(phrase, freq, pinyin) VALUES(?, ?, ?)', (k, entropy, pinyin))
    del unigram
    gc.collect(2)

    log.close()


    total_bigram  = 0
    print('loading: bigram.cache')
    bigram  = file_get_cache('bigram.cache')
    #bigram  = file_get_json('bigram.json')
    for first, second, cnt in bigram:
        total_bigram = total_bigram + cnt

    print('insert bigram into sqlite3 db')
    print(' bigram  =', total_bigram)
    max_entropy = 0
    min_entropy = 0
    for k1, k2, v in bigram:
        entropy = -math.log(v/total_bigram)
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


