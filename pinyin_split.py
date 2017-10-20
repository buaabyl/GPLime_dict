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
import types
import json
import math

PINYIN_CONSONANT = {
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
}

PINYIN_VOWEL = {
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

def load_model(fn):
    valid_pinyin = {}
    for k, vowels in VALID_PAIRS.items():
        for vowel in vowels:
            valid_pinyin[k + "'" + vowel] = (k, vowel)

    f = open(fn)
    m = json.loads(f.read())
    f.close()

    list_to_delete = []

    # check pinyin in unigram is valid pair
    for k, freq in m.items():
        if k not in valid_pinyin:
            list_to_delete.append(k)
    for k in list_to_delete:
        del m[k]

    # check all valid pair appear at least one time
    for k in valid_pinyin:
        if k not in m:
            m[k] = 1

    # convert counter to probability
    total = 0
    for k, freq in m.items():
        total = total + freq
    total = total + len(m)

    # add 1 to every counter
    model = {'': 0}
    for k, freq in m.items():
        p = (freq + 1) / total
        logp = -math.log(p)
        model[k] = logp

        newk = k.replace("'", '')
        newk = newk.replace(" ", '')
        if newk != k:
            model[newk] = logp

    return model


'''
1. Build a multi-leaf tree
2. Flat it to a list
3. Sort it by probability?
4. Howto porting to c library.
'''
def lexcial_get_all_possible(s, depth=0):
    if not s or s == '':
        return None

    if len(s) == 1:
        return [(s, None)]

    l = []

    PINYINS = {}
    max_pinyin_len = 0
    for consonant, vowels in VALID_PAIRS.items():
        for vowel in vowels:
            if consonant == ' ':
                consonant = ''
            pinyin = consonant + vowel
            PINYINS[pinyin] = (consonant, vowel)
            if len(pinyin) > max_pinyin_len:
                max_pinyin_len = len(pinyin)


    if len(s) < max_pinyin_len:
        max_pinyin_len = len(s)

    while max_pinyin_len > 0:
        substr = s[:max_pinyin_len]
        if substr in PINYINS:
            l.append((substr, lexcial_get_all_possible(s[max_pinyin_len:], depth+1)))
        max_pinyin_len = max_pinyin_len - 1

    if len(l) == 0:
        prefix = s[0]
        suffix = s[1:]
        if prefix in PINYIN_CONSONANT:
            res = lexcial_get_all_possible(suffix, depth+1)
            l.append((prefix, res))

        if len(s) > 2:
            prefix = s[0:2]
            suffix = s[2:]
            if prefix in PINYIN_CONSONANT:
                res = lexcial_get_all_possible(suffix, depth+1)
                l.append((prefix, res))

    if len(l) == 0:
        return None

    return l


def flat_possible_tree(res, depth=0):
    l = []
    if not res:
        return None
    if isinstance(res, list):
        for record in res:
            sublist = flat_possible_tree(record, depth+1)
            if not sublist:
                continue
            l.extend(sublist)
        return l
    elif isinstance(res, tuple):
        sublist = flat_possible_tree(res[1], depth+1)
        if not sublist:
            return [res[0]]
        for subrecord in sublist:
            l.append(res[0]+ ',' + subrecord)
        return l
    else:
        #this must not reach...
        raise "Invalid format"

def dump_possible_tree(res, prefix='  '):
    if not res:
        return
    if isinstance(res, list):
        for record in res:
            dump_possible_tree(record, prefix)
    elif isinstance(res, tuple):
        msg = prefix + '+' + res[0]
        print(msg)
        dump_possible_tree(res[1], prefix + '| ' + ' ' * len(res[0]))
    else:
        print('???')

def sort_candidates(candidates, model):
    PINYINS = {}
    for consonant, vowels in VALID_PAIRS.items():
        for vowel in vowels:
            if consonant == ' ':
                consonant = ''
            pinyin = consonant + vowel
            PINYINS[pinyin] = (consonant, vowel)

    l = []
    for candidate in candidates:
        phrases = candidate.split(',')
        rank = 0
        for phrase in phrases:
            if phrase in PINYINS:
                rank = rank + 1
            else:
                rank = rank - 1

        prob = 0
        for phrase in phrases:
            if phrase in model:
                prob = prob + model[phrase]
            else:
                prob = prob + model['']
        prob_avg = prob / len(phrases)

        l.append((rank, prob_avg, candidate))

    l.sort(key=lambda v:1000 * v[0] + v[1], reverse=True)

    return l

if __name__ == '__main__':
    model = load_model('pinyin.unigram')

    testcases = {
            "lian"                           : '连/李安',
            "liangen"                        : '恋歌/李安格',
            "zheshiyigejiandandeceshiyongli" : '这 是 一个 简单的 测试 用例',
            "zhonghuarenmingongheguo"        : '中华人民共和国',
            "zhonghrmgongheg"                : '中华人民共和国',
            "zhhuarmgheguo"                   : '中华人民共和国',
            "zhrmghg"                        : '中华人民共和国',
            "zzifwijvvu"                     : ''
    }

    for k, v in testcases.items():
        print('STRING:', k)

        res = lexcial_get_all_possible(k)
        #dump_possible_tree(res)
        print('res:')
        candidates = flat_possible_tree(res)
        l = sort_candidates(candidates, model)
        for rank, prob, candidate in l:
            print(' %3d: %.3f, %s' % (rank, prob, candidate))
        print()

