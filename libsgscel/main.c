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
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "libsgscel.h"

static void _puts(FILE* fp, uint8_t* str)
{
    for (;*str != '\0';str++) {
        if (*str == '\r') {
            continue;
        } else if (*str == '\n') {
            fprintf(fp, "# ");
        } else {
            fprintf(fp, "%c", *str);
        }
    }
    fprintf(fp, "\n");
}


int main(int argc, const char* argv[])
{
    sgscel_db_t* db;
    const sgscel_word_t* word;
    double max_frequency = 0;
    int nr_words = 0;
    char lst_file_name[4096];
    FILE* fp;

    if (argc != 2) {
        printf("Usage: %s test.scel\n", argv[0]);
        return -1;
    } 

    db = sgscel_load(argv[1]);
    if (db != NULL) {
        strcpy(lst_file_name, argv[1]);
        strcat(lst_file_name, ".lst");
        if ((fp = fopen(lst_file_name, "w")) == NULL) {
            fp = stdout;
        } else {
            printf("write \"%s\"\n", lst_file_name);
        }

        fprintf(fp, "# vim: set fileencoding=utf-8\n");
        fprintf(fp, "# -*- coding:utf-8 -*-\n");
        fprintf(fp, "#\n");
        fprintf(fp, "# @name         : %s\n", db->name);
        fprintf(fp, "# @category     : %s\n", db->category);
        fprintf(fp, "# @description  : "); _puts(fp, db->description);
        fprintf(fp, "# @example      : "); _puts(fp, db->example);

        for (word = db->words;word != NULL;word = word->next) {
            nr_words++;
            if (word->frequency > max_frequency) {
                max_frequency = word->frequency;
            }
        }
        max_frequency = max_frequency + 1;
        fprintf(fp, "# @count        : %d\n", nr_words);
        fprintf(fp, "# @frequency    : %.0f\n", max_frequency);
        fprintf(fp, "\n");

        for (word = db->words;word != NULL;word = word->next) {
            fprintf(fp, "%s %s %.6f\n", word->pinyin, word->string, word->frequency/max_frequency);
        }

        sgscel_destroy(db);

        if (fp != stdout) {
            fclose(fp);
        }
    }

    return 0;
}


