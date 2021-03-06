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
import sys
import os
import re
import getopt
import glob
import json 
import operator
from mako.template import Template

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


header = '''\
/* vim: set fileencoding=utf-8:
 * 
 *                   GNU GENERAL PUBLIC LICENSE
 *                       Version 2, June 1991
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; see the file COPYING.  If not, write to
 * the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
 *
 * @author  buaabyl@gmail.com
 * @ref sunpinyin
 */
#ifndef PINYIN_UTILS_H_F26EFD02_9BB5_5D72_A873_F6574E145C2A_INCLUDED_
#define PINYIN_UTILS_H_F26EFD02_9BB5_5D72_A873_F6574E145C2A_INCLUDED_

/*
 * @retval -1   error
 * @return      internal defined id for consonant and vowel
 */
int lime_str_to_id(const char* s);


#endif

'''


tpl = '''\
/* vim: set fileencoding=utf-8:
 * 
 *                   GNU GENERAL PUBLIC LICENSE
 *                       Version 2, June 1991
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; see the file COPYING.  If not, write to
 * the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
 *
 * @author  buaabyl@gmail.com
 * @ref sunpinyin
 *
 *  2012.10.01
 *      I read sunpinyin source code, and design this library,
 *      so the license must be GPL or LGPL
 *      implement it in flex+bison
 *
 *  2017.04.16
 *      rewrite by hand, remove flex and bison
 *      optimize
 *
 *  2017.08.01
 *      optimize
 *
 *  2017.10.20
 *      rewrite
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include "pinyin_utils.h"

#define LIME_MAX_PINYIN_LENGTH  ${model['max_pinyin_len']}
#define LIME_MAX_CONSONANT_ID   ${model['max_consonant_id']}
#define LIME_MAX_VOWEL_ID       ${model['max_vowel_id']}

// it is not critical operation, NO NEED to using hash map!
// JUST simple compare is enough.
int lime_str_to_id(const char* s)
{
    const uint32_t LUT[] = {
        // value        ID  original_string
% for k, id_, v in str2id_list:
        ${'0x%08x' % v},   //${'%2d' % id_}, ${k}
% endfor
    };
    int i;
    int n;
    uint32_t v;

    n = strlen(s);
    if (n > 4) {
        return -1;
    }

    v = 0;
    for (i = 0;i < n;i++) {
        v = (v << 8) | s[i];
    }

    for (i = 0;i < ${len(str2id_list) + 1};i++) {
        if (LUT[i] == v) {
            return i + 1;
        }
    }

    return -1;
}


'''



if __name__ == '__main__':
    PINYINS = {}
    for consonant, vowels in VALID_PAIRS.items():
        for vowel in vowels:
            pinyin = consonant + "'" + vowel
            PINYINS[pinyin] = (consonant, vowel)

    max_pinyin_len   = 0
    max_consonant_id = 23
    max_vowel_id     = 56

    PINYINS_COMPACT = {}
    for consonant, vowels in VALID_PAIRS.items():
        for vowel in vowels:
            if consonant == ' ':
                consonant = ''
            pinyin = consonant + vowel
            PINYINS_COMPACT[pinyin] = (consonant, vowel)
            if len(pinyin) > max_pinyin_len:
                max_pinyin_len = len(pinyin)

    f = open('pinyin.json', 'w')
    m = {
            'max_pinyin_len': max_pinyin_len,
            'max_consonant_id': max_consonant_id,
            'max_vowel_id': max_vowel_id,
            'consonant': PINYIN_CONSONANT,
            'vowel': PINYIN_VOWEL,
            'pair': VALID_PAIRS,
            'lookup': PINYINS,
            'compact': PINYINS_COMPACT,
    }
    f.write(json.dumps(m, indent=4))
    f.close()
    print('wrote to "pinyin.json"')

    str2id_list = []
    for k, id_ in sorted(PINYIN_CONSONANT.items(), key=operator.itemgetter(1)):
        v = 0
        for c in k:
            v = (v << 8) | ord(c)
        str2id_list.append((k, id_, v))

    for k, id_ in sorted(PINYIN_VOWEL.items(), key=operator.itemgetter(1)):
        v = 0
        for c in k:
            v = (v << 8) | ord(c)
        str2id_list.append((k, id_, v))

    f = open('pinyin_utils.h', 'w')
    f.write(header)
    f.close()
    print('wrote to "pinyin_utils.h"')

    h = Template(tpl)
    d = h.render_unicode(model = m, str2id_list = str2id_list)
    f = open('pinyin_utils.c', 'w')
    f.write(d)
    f.close()
    print('wrote to "pinyin_utils.c"')


