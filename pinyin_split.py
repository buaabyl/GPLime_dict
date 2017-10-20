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

def load_model():
    f = open('pinyin.json', 'r')
    model = json.loads(f.read())
    f.close()

    f = open('pinyin.unigram')
    unigram = json.loads(f.read())
    f.close()

    # verify pinyin unigram
    list_to_delete = []
    for k, freq in unigram.items():
        if k not in model['lookup']:
            print('missing', k)
            list_to_delete.append(k)
    for k in list_to_delete:
        del unigram[k]

    # check all valid pair appear at least one time
    for k in model['lookup']:
        if k not in unigram:
            unigram[k] = 1

    # convert counter to probability
    total = 0
    for k, freq in unigram.items():
        total = total + freq
    total = total + len(unigram)

    # add 1 to every counter
    probability = {'': 0}
    for k, freq in unigram.items():
        p = (freq + 1) / total
        logp = -math.log(p)
        probability[k] = logp

        newk = k.replace("'", '')
        newk = newk.replace(" ", '')
        if newk != k:
            probability[newk] = logp

    model['probability'] = probability

    f = open('pinyin.model', 'w')
    f.write(json.dumps(model, indent=4))
    f.close()

    return model

def lexcial_get_all_possible(s, model, depth=0):
    if not s or s == '':
        return None

    if len(s) == 1:
        return [(s, None)]

    l = []

    max_pinyin_len = model['max_pinyin_len']
    if len(s) < max_pinyin_len:
        max_pinyin_len = len(s)

    while max_pinyin_len > 0:
        substr = s[:max_pinyin_len]
        if substr in model['compact']:
            l.append((substr, lexcial_get_all_possible(s[max_pinyin_len:], model, depth+1)))
        max_pinyin_len = max_pinyin_len - 1

    if len(l) == 0:
        prefix = s[0]
        suffix = s[1:]
        if prefix in model['consonant']:
            res = lexcial_get_all_possible(suffix, model, depth+1)
            l.append((prefix, res))

        if len(s) > 2:
            prefix = s[0:2]
            suffix = s[2:]
            if prefix in model['consonant']:
                res = lexcial_get_all_possible(suffix, model, depth+1)
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
    l = []
    probability_map = model['probability']

    for candidate in candidates:
        phrases = candidate.split(',')
        rank = 0
        for phrase in phrases:
            if phrase in model['compact']:
                rank = rank + 1
            else:
                rank = rank - 1

        prob = 0
        for phrase in phrases:
            if phrase in probability_map:
                prob = prob + probability_map[phrase]
            else:
                prob = prob + probability_map['']
        prob_avg = prob / len(phrases)

        l.append((rank, prob_avg, candidate))

    l.sort(key=lambda v:1000 * v[0] + v[1], reverse=True)

    return l


if __name__ == '__main__':
    model = load_model()

    testcases = {
            "lian"                           : '连/李安',
            "liangen"                        : '恋歌/李安格',
            "zheshiyigejiandandeceshiyongli" : '这 是 一个 简单的 测试 用例',
            "zhonghuarenmingongheguo"        : '中华人民共和国',
            "zhonghrmgongheg"                : '中华人民共和国',
            "zhhuarmgheguo"                  : '中华人民共和国',
            "zhrmghg"                        : '中华人民共和国',
            "zzifwijvvu"                     : ''
    }

    for k, v in testcases.items():
        print('STRING:', k)

        res = lexcial_get_all_possible(k, model)
        #dump_possible_tree(res)
        print('res:')
        candidates = flat_possible_tree(res)
        l = sort_candidates(candidates, model)
        for rank, prob, candidate in l:
            print(' %3d: %.3f, %s' % (rank, prob, candidate))
        print()



