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

#define LIME_MAX_PINYIN_LENGTH  6
#define LIME_MAX_CONSONANT_ID   23
#define LIME_MAX_VOWEL_ID       56

// it is not critical operation, NO NEED to using hash map!
// JUST simple compare is enough.
int lime_str_to_id(const char* s)
{
    const uint32_t LUT[] = {
        // value        ID  original_string
        0x00000062,   // 1, b
        0x00000063,   // 2, c
        0x00006368,   // 3, ch
        0x00000064,   // 4, d
        0x00000066,   // 5, f
        0x00000067,   // 6, g
        0x00000068,   // 7, h
        0x0000006a,   // 8, j
        0x0000006b,   // 9, k
        0x0000006c,   //10, l
        0x0000006d,   //11, m
        0x0000006e,   //12, n
        0x00000070,   //13, p
        0x00000071,   //14, q
        0x00000072,   //15, r
        0x00000073,   //16, s
        0x00007368,   //17, sh
        0x00000074,   //18, t
        0x00000077,   //19, w
        0x00000078,   //20, x
        0x00000079,   //21, y
        0x0000007a,   //22, z
        0x00007a68,   //23, zh
        0x00000061,   //24, a
        0x00006169,   //25, ai
        0x0000616e,   //26, an
        0x00616e67,   //27, ang
        0x0000616f,   //28, ao
        0x00000065,   //29, e
        0x00006569,   //30, ei
        0x0000656e,   //31, en
        0x00656e67,   //32, eng
        0x00006572,   //33, er
        0x00000069,   //34, i
        0x00006961,   //35, ia
        0x0069616e,   //36, ian
        0x69616e67,   //37, iang
        0x0069616f,   //38, iao
        0x00006965,   //39, ie
        0x0000696e,   //40, in
        0x00696e67,   //41, ing
        0x696f6e67,   //42, iong
        0x00006975,   //43, iu
        0x0000006f,   //44, o
        0x006f6e67,   //45, ong
        0x00006f75,   //46, ou
        0x00000075,   //47, u
        0x00007561,   //48, ua
        0x00756169,   //49, uai
        0x0075616e,   //50, uan
        0x75616e67,   //51, uang
        0x00007565,   //52, ue
        0x00007569,   //53, ui
        0x0000756e,   //54, un
        0x0000756f,   //55, uo
        0x00000076,   //56, v
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

    for (i = 0;i < 57;i++) {
        if (LUT[i] == v) {
            return i + 1;
        }
    }

    return -1;
}


