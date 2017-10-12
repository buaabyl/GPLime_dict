
## unigram.cache:
这两个cache保存的是出现的次数，未作处理

    map<phrase:=string, counter:=int>

## bigram.cache:   
这两个cache保存的是出现的次数，未作处理

    map<phrase:=string, counter:=int>


## ngram_chs.db
保存处理后的结果，其中logp是 `-log(count(phrase0+phrase1)/count(phrase0))` 这样的数据。

    CREATE TABLE unigram(phrase TEXT, freq REAL, pinyin TEXT)
    CREATE TABLE unigram_count(value INTEGER)
    CREATE TABLE bigram(phrase0 TEXT, phrase1 TEXT, logp REAL)





