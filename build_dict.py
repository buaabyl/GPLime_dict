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
import gc
import sys
import os
import re
import getopt
import glob
import json
import stat
import pickle

PINYIN_LUT = {
    # consonant
    ' '   : 0,  # '_' is equal to space
    'b'   : 1,
    'c'   : 2,
    'ch'  : 3,
    'd'   : 4,
    'f'   : 5,
    'g'   : 6,
    'h'   : 7,
    'j'   : 8,
    'k'   : 9,
    'l'   : 10,
    'm'   : 11,
    'n'   : 12,
    'p'   : 13,
    'q'   : 14,
    'r'   : 15,
    's'   : 16,
    'sh'  : 17,
    't'   : 18,
    'w'   : 19,
    'x'   : 20,
    'y'   : 21,
    'z'   : 22,
    'zh'  : 23,

    #vowel
    'a'   : 24,
    'ai'  : 25,
    'an'  : 26,
    'ang' : 27,
    'ao'  : 28,
    'e'   : 29,
    'ei'  : 30,
    'en'  : 31,
    'eng' : 32,
    'er'  : 33,
    'i'   : 34,
    'ia'  : 35,
    'ian' : 36,
    'iang': 37,
    'iao' : 38,
    'ie'  : 39,
    'in'  : 40,
    'ing' : 41,
    'iong': 42,
    'iu'  : 43,
    'o'   : 44,
    'ong' : 45,
    'ou'  : 46,
    'u'   : 47,
    'ua'  : 48,
    'uai' : 49,
    'uan' : 50,
    'uang': 51,
    'ue'  : 52,
    'ui'  : 53,
    'un'  : 54,
    'uo'  : 55,
    'v'   : 56,
}

VALID_PAIRS = {
    " " :  ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "er", "o", "ou"],
    "b" :  ["a", "ai", "an", "ang", "ao", "ei", "en", "eng", "i", "ian", "iao", "ie", "in", "ing", "o", "u"],
    "p" :  ["a", "ai", "an", "ang", "ao", "ei", "en", "eng", "i", "ian", "iao", "ie", "in", "ing", "o", "ou", "u"],
    "m" :  ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ian", "iao", "ie", "in", "ing", "iu", "o", "ou", "u"],
    "f" :  ["a", "an", "ang", "ei", "en", "eng", "iao", "o", "ou", "u"],
    "d" :  ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ia", "ian", "iao", "ie", "ing", "iu", "ong", "ou", "u", "uan", "ui", "un", "uo"],
    "t" :  ["a", "ai", "an", "ang", "ao", "e", "ei", "eng", "i", "ian", "iao", "ie", "ing", "ong", "ou", "u", "uan", "ui", "un", "uo"],
    "n" :  ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ian", "iang", "iao", "ie", "in", "ing", "iu", "ong", "ou", "u", "uan", "un", "uo", "v", "ue"],
    "l" :  ["a", "ai", "an", "ang", "ao", "e", "ei", "eng", "i", "ia", "ian", "iang", "iao", "ie", "in", "ing", "iu", "o", "ong", "ou", "u", "uan", "un", "uo", "v", "ue"],
    "g" :  ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "ong", "ou", "u", "ua", "uai", "uan", "uang", "ui", "un", "uo"],
    "k" :  ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "ong", "ou", "u", "ua", "uai", "uan", "uang", "ui", "un", "uo"],
    "h" :  ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "ong", "ou", "u", "ua", "uai", "uan", "uang", "ui", "un", "uo"],
    "j" :  ["i", "ia", "ian", "iang", "iao", "ie", "in", "ing", "iong", "iu", "u", "uan", "ue", "un"],
    "q" :  ["i", "ia", "ian", "iang", "iao", "ie", "in", "ing", "iong", "iu", "u", "uan", "ue", "un"],
    "x" :  ["i", "ia", "ian", "iang", "iao", "ie", "in", "ing", "iong", "iu", "u", "uan", "ue", "un"],
    "zh":  ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ong", "ou", "u", "ua", "uai", "uan", "uang", "ui", "un", "uo"],
    "ch":  ["a", "ai", "an", "ang", "ao", "e", "en", "eng", "i", "ong", "ou", "u", "ua", "uai", "uan", "uang", "ui", "un", "uo"],
    "sh":  ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ou", "u", "ua", "uai", "uan", "uang", "ui", "un", "uo"],
    "r" :  ["an", "ang", "ao", "e", "en", "eng", "i", "ong", "ou", "u", "ua", "uan", "ui", "un", "uo"],
    "z" :  ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ong", "ou", "u", "uan", "ui", "un", "uo"],
    "c" :  ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ong", "ou", "u", "uan", "ui", "un", "uo"],
    "s" :  ["a", "ai", "an", "ang", "ao", "e", "en", "eng", "i", "ong", "ou", "u", "uan", "ui", "un", "uo"],
    "y" :  ["a", "an", "ang", "ao", "e", "i", "in", "ing", "o", "ong", "ou", "u", "uan", "ue", "un"],
    "w" :  ["a", "ai", "an", "ang", "ei", "en", "eng", "o", "u"],
}

PINYIN_MAP = {}

def init():
    for consonant, vowels in VALID_PAIRS.items():
        for vowel in vowels:
            pinyin = consonant + vowel
            if pinyin in PINYIN_MAP:
                raise 'Duplicate!'
            PINYIN_MAP[pinyin] = (consonant, vowel)


def load_lst_file(fn):
    f = open(fn, 'r', encoding='UTF-8')
    d = f.read()
    f.close()

    meta = {
            'name'      :'noname',
            'category'  :'test',
            'count'     :'0',
            'frequency' :'10000'
    }

    l = []

    pattern = re.compile(r'^#\W*@(.+?)\W*:\W*(.+?)$')

    lines = d.splitlines()
    for line in lines:
        if len(line) == 0:
            continue
        if line[0] == '#':
            res = pattern.match(line)
            if res:
                if res.groups()[0] in meta:
                    if res.groups()[0] == 'frequency':
                        if float(res.groups()[1]) < 10000:
                            meta[res.groups()[0]] = res.groups()[1]
                    else:
                        meta[res.groups()[0]] = res.groups()[1]
        else:
            tokens = re.split('[ \t]+', line)
            if len(tokens) != 3:
                print(tokens)
                raise 'Invalid value'

            pinyins = tokens[0].split(",")
            words   = tokens[1]
            freq    = float(tokens[2]) * float(meta['frequency'])

            new_pinyins = []
            for pinyin in pinyins:
                pinyin = pinyin.replace('_', ' ')
                if "'" in pinyin:
                    new_pinyins.append(pinyin.split("'"))
                else:
                    if pinyin not in PINYIN_MAP:
                        pinyin = ' ' + pinyin
                    if pinyin not in PINYIN_MAP:
                        print(pinyin, words, freq)
                        raise 'Unknown pinyin sequency'

                    new_pinyins.append(PINYIN_MAP[pinyin])
            pinyins = None

            l.append((new_pinyins, words, freq))

    return (meta, l)

def load_lst_files(lst_files):
    pinyin_dbs = []

    for fn in lst_files:
        update_cache = False 
        cache_fn = fn + '.cache'
        if not os.path.isfile(cache_fn):
            update_cache = True
        elif os.stat(cache_fn)[stat.ST_MTIME] < os.stat(fn)[stat.ST_MTIME]:
            update_cache = True
    
        if update_cache:
            print('*', fn, '(loading...)')
            (meta, l) = load_lst_file(fn)
            print(' ', meta)
            print(' ', cache_fn, '(updated)')
            #jstr = json.dumps(l, ensure_ascii=False, indent=4)
            jstr = pickle.dumps(l)
            #f = open(cache_fn, 'w', encoding='UTF-8')
            f = open(cache_fn, 'wb')
            f.write(jstr)
            f.close()

            pinyin_dbs.append(l)
        else:
            print('*', fn, '(cache)')
            #f = open(cache_fn, 'r', encoding='UTF-8')
            f = open(cache_fn, 'rb')
            d = f.read()
            f.close()
            #l = json.loads(d)
            l = pickle.loads(d)
            pinyin_dbs.append(l)

    return pinyin_dbs


def merge_pinyins(pinyin_dbs):
    dbs_by_length = []
    for i in range(32):
        dbs_by_length.append({})

    nr_totals = len(pinyin_dbs)
    i = 0

    nr_valid  = 0
    nr_skip   = 0

    for l in pinyin_dbs:
        i = i + 1
        print('* merge %d/%d' % (i, nr_totals))
        for pinyins, words, freq in l:
            n = len(pinyins)
            if n >= 32:
                print('Warning %d of words is too long' % n)
                continue
            db = dbs_by_length[n]

            k = ','.join(["'".join(kv) for kv in pinyins]) + '|' + words
            if k not in db:
                db[k] = freq
                nr_valid = nr_valid + 1
            if db[k] < freq:
                db[k] = freq
                nr_skip = nr_skip + 1

    print('* processed: valids %d words, skip %d words. (%.3f%%)' % \
            (nr_valid, nr_skip, 100 % nr_valid / (nr_valid + nr_skip)))

    return dbs_by_length

if __name__ == '__main__':
    init()

    lst_files = []
    if len(sys.argv) > 1:
        lst_files.extend(sys.argv[1:])
    else:
        for prefix, dirs, files in os.walk('.'):
            for fn in files:
                if os.path.splitext(fn)[1].lower() == '.lst':
                    lst_files.append(os.path.join(prefix, fn))

    pinyin_dbs = load_lst_files(lst_files)
    gc.collect()

    db = merge_pinyins(pinyin_dbs)
    pinyin_dbs = None
    gc.collect()

    # debug
    f = open('debug.log', 'w', encoding='UTF-8')
    for db_sub in db:
        for k, freq in db_sub.items():
            f.write('%-10.0f |%s\n' % (freq, k))
    f.close()

    f = open('jieba.dict', 'w', encoding='UTF-8')
    for db_sub in db:
        for k, freq in db_sub.items():
            chs = k.split('|')[1]
            f.write('%s %.0f\n' % (chs, freq))
    f.close()



