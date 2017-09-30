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

def is_consonant(s):
    if not s:
        return False
    return s in PINYIN_CONSONANT

def is_vowel(s):
    if not s:
        return False
    return s in PINYIN_VOWEL

def is_independent_vowel(s):
    if not s:
        return False
    return s in ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "er", "o", "ou"]

def is_valid_pair(consonant, vowel):
    if consonant not in VALID_PAIRS:
        return False
    if vowel not in VALID_PAIRS[consonant]:
        return False
    return True 

'''
@breif      split input sequences to independent consonant and vowel
@return     a list of possible pinyin pair, each consonant or vowel divided by "'"
'''
def lexcial_analysis(s, depth=0):
    MAX_PINYIN = 6

    # clean typo input like this: "'''"
    if depth == 0:
        s = re.sub(r"[']+", "'", s)

    if s.startswith("'"):
        s = s[1:]

    l = []

    n = len(s)
    if n == 0:
        return None
    if n > MAX_PINYIN:
        n = MAX_PINYIN
    while n > 0:
        k = s[:n]
        if is_consonant(k) or is_vowel(k):
            suffix = s[n:]
            if len(suffix) == 0:
                l.append(k)
            else:
                res = lexcial_analysis(suffix, depth+1)
                if not res:
                    return None
                else:
                    for item in res:
                        l.append("%s|%s" % (k, item))
        n = n - 1

    return l


def parse_and_filter(model, list_pinyins):
    list_of_candidates = []

    index = 0

    for pinyins in list_pinyins:
        tokens = pinyins.split("|")
        tokens.append(None)

        i = 0
        n = len(tokens)
        error = False
        list_of_pair = []
        while i < n-1:
            k1 = tokens[i]
            k2 = tokens[i+1]

            # last token
            if not k2:
                if is_consonant(k1):
                    list_of_pair.append("%s'" % (k1))
                elif is_vowel(k1) and is_independent_vowel(k1):
                    list_of_pair.append("'%s" % (k1))
                else:
                    error = True
                break

            if is_consonant(k1) and is_vowel(k2) and is_valid_pair(k1, k2):
                list_of_pair.append("%s'%s" % (k1, k2))
                i = i + 2
            elif is_consonant(k1):
                list_of_pair.append("%s'" % (k1))
                i = i + 1
            elif is_vowel(k1) and is_independent_vowel(k1):
                list_of_pair.append(" '%s" % (k1))
                i = i + 1
            else:
                error = True
                break

        if error:
            print('    Warning: remove this candidate:', tokens)
            continue

        P = 0
        for pinyin in list_of_pair:
            if pinyin in model:
                P = P + model[pinyin]
            else:
                P = P + model['']

        list_of_candidates.append((P, list_of_pair))
        
        index = index + 1

    list_of_candidates.sort(key=lambda v:v[0])

    return list_of_candidates

def create_pinyin_for_candidates(model, list_of_candidates):
    for P, list_of_pair in res:
        l = []
        for pinyin in list_of_pair:
            consonant, vowel = pinyin.split("'")
            if consonant and vowel:
                continue
            if consonant:
                print('  [' + pinyin + '] to find vowel')
            else:
                print('  [' + pinyin + '] to find consonant')



if __name__ == '__main__':
    model = load_model('pinyin.unigram')

    l = [
        "lian",     # li'an, lian
        "livn",     # typo
        #"li'an",    # li'an
        #"liang",    # li'ang, liang, li'an'g
        #"li'ang",
        #"lii",      #typo
        #"liyi",     #typo
        #"li3",      #typo
        #"ceshiyixia",
        #"chesiyixia",
        #"zhonghuarmghguo",
    ]

    for s in l:
        print('-' * 80)
        print('input:', s)
        res = lexcial_analysis(s)
        if not res:
            print('    Lexcial error')
            print()
            continue
        print('lexcial: %d' % len(res))
        i = 0
        for item in res:
            print('    %2d: %s' % (i, item))
            i = i + 1



        print('parse:')
        res = parse_and_filter(model, res)
        if not res:
            print('    Parser error')
            print()
            continue
        for P, list_of_pair in res:
            print('%12.6f: %s' % (P, '|'.join(list_of_pair)))
        print()



        print('fill:')
        res = create_pinyin_for_candidates(model, res)
        print()


        #res.sort(key=lambda v:len(v.split("'")))

        #jstr = json.dumps(res, indent=4)
        #print(s)
        #print(jstr)
        #print()


