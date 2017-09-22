# GPLime_dict
Directory of dictionary for GPLime

@ref http://googleresearch.blogspot.com/2006/08/all-our-n-gram-are-belong-to-you.html \
@ref https://www.ldc.upenn.edu/language-resources/data/obtaining \
@ref https://stanfordnlp.github.io/CoreNLP/ \
@ref https://github.com/fxsjy/jieba \
@ref https://github.com/yanyiwu/cppjieba \
@ref https://github.com/qinwf/BigDict \
@ref https://yanyiwu.com/work/2015/06/14/jieba-series-performance-test.html \
@ref http://www.52nlp.cn 

## 备忘

首先调用 `bigdict_collections/preprocess.py` 和 `WORDS2PINYINS.cache` 两个文件。
其中 `jieba.dict` 这个大词库，用于python的jieba分词库。
而 `WORDS2PINYINS.cache` 用于通过汉字反查拼音。

调用 `bigdict_collections/article2ngram.py` 把新闻样本转换成 unigram.cache 和 bigram.cache 两个文件。
调用 `bigdict_collections/ngram2sqlite3_chs.py` 加载 `jieba.dict` ，处理没有出现的词语，
并把 unigram.cache 和 bigram.cache 存到数据库里。
```sql
CREATE TABLE unigram(phrase TEXT, freq REAL, pinyin TEXT)
CREATE TABLE unigram_count(value INTEGER)
CREATE TABLE bigram(phrase0 TEXT, phrase1 TEXT, logp REAL)
```


英文是独立的，调用 `ngram_enu/text2ngram.py` 将BBC的news数据 bbc_dump.json 解析，
生成 unigram.json 和 bigram.json 两个文件。然后调用 `ngram_enu/ngram2sqlite3.py` 
加载这两个json文件，并且在同时加载google的单词列表，处理bbc里没有出现的词语。
然后把结果保存成sqlite3数据库。
```sql
CREATE TABLE unigram(phrase TEXT, logp REAL);
CREATE TABLE bigram(phrase0 TEXT, phrase1 TEXT, logp REAL);
```
logp是频率p做了处理 `-log(p)` 之后再保存的。



最终得到的是两个数据库： `ngram_enu.db` 和 `ngram_chs.db`





