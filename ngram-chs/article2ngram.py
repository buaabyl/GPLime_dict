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

if __name__ == '__main__':
    list_of_articles = get_all_articles()

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
    file_put_json('unigram.json', l)
    print('wrote to unigram.json')


    print('bigram', len(bigram))
    l = []
    for k,v in bigram.items():
        first, second = k.split(' ')
        l.append((first, second, v))
    l = sorted(l, key=lambda v:v[2], reverse=True)
    file_put_json('bigram.json', l)
    print('wrote to bigram.json')

    gc.collect(2)

    dbname = 'ngram_chs.db'
    print('write to', dbname) 
    if os.path.exists(dbname):
        os.remove(dbname)
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

    db = sqlite3.connect(dbname)
    cur = db.cursor()
    cur.execute('CREATE TABLE unigram(phrase TEXT, freq REAL)')
    cur.execute('CREATE TABLE bigram(phrase0 TEXT, phrase1 TEXT, freq REAL)')

    print('insert unigram into sqlite3 db')
    for k, v in unigram:
        entropy = -math.log(v/total_unigram)
        cur.execute('INSERT INTO unigram(phrase, freq) VALUES(?, ?)', (k, entropy))

    print('insert bigram into sqlite3 db')
    for k1, k2, v in bigram:
        entropy = -math.log(v/total_bigram)
        cur.execute('INSERT INTO bigram(phrase0, phrase1, freq) VALUES(?, ?, ?)', (k1, k2, entropy))

    db.commit()

    print('create index')
    cur.execute('CREATE INDEX index_bigram ON bigram(phrase0, phrase1)')
    db.commit()


