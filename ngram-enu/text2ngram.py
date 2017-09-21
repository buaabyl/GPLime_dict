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
# @cite Manning, Christopher D., Mihai Surdeanu, John Bauer, Jenny Finkel, Steven J. Bethard, and David McClosky. 2014.
#   The Stanford CoreNLP Natural Language Processing Toolkit In Proceedings of
#   the 52nd Annual Meeting of the Association for Computational Linguistics: 
#   System Demonstrations, pp. 55-60. [pdf] [bib]
#
# @author william bao
# 0.0.1 simplest implementation
# TODO: learning stanford NLP lesson, and try again later.
#       Take care of `syllable`, `Case folding`, and `Stemming` and `Lemmatization` too.
#       Preprocess of corpus is important, all fellowing processes based on it.
#       We will get misunderstanding model when ignore all above.
#       
#       This demo converted all char to lowcase, but `BBC` is beter than `bbc`.
#       We need to determine which word is better.
#
# 0.0.2 add index to sqlite3, but the size of db increased, twice bigger...
#
import sys
import os
import re
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

def strip_nonenglish(s):
    s = s.replace("'s", " is")
    s = s.replace("'m", " am")
    s = s.replace("don't", "do not")
    s = s.replace("didn't", "did not")
    s = s.replace("'ll", " will")
    l = []
    for c in s:
        if ord(c) > 0x80:
            l.append(' ')
        else:
            l.append(c.lower())

    return ''.join(l)

if __name__ == '__main__':
    f = open('bbc_dump.json', 'r', encoding='utf-8')
    jstr = f.read()
    f.close()

    list_of_articles = json.loads(jstr)

    unigram = {}
    bigram = {}
    N = len(list_of_articles)
    nr_processed = 0
    for year, month, lines in list_of_articles:
        msg = '%5.2f%% (%d/%d)\r' % (100 * nr_processed / N, nr_processed, N)
        sys.stdout.write(msg)
        nr_processed = nr_processed + 1
        #if nr_processed == 100:
        #    break

        for line in lines:
            line = strip_nonenglish(line)

            sentences = re.split(r'[,.?!]', line)
            
            for sentence in sentences:
                #res = jieba.cut(sentence)
                res = nltk.word_tokenize(sentence)

                previous = None
                for token in res:
                    #if re.match(r'\W+', token):
                    if not re.match(r'[0-9a-zA-Z_-]', token):
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


    dbname = 'ngram_enu.db'
    print('wrote to', dbname) 
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

    


