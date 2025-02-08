from typing import Optional
from fastapi import FastAPI, Depends
import sqlite3

app = FastAPI()

def get_db():
    try:
        conn = sqlite3.connect('bible.db', check_same_thread=False)
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        conn.close()

@app.get("/")
def read_root():
    return "Test query API"

@app.get("/query/{word}")
def read_item(word: str, conn = Depends(get_db)):
    
    results = {}
    
    for row in conn.execute("""
        select w.word as baseword, formnum, pos, inner, w2.word as subword
        from formations f
        join words w on w.wordid = f.baseword
        join words w2 on w2.wordid = f.subword
        where w.word = ?
    """,(word,)):
        formnum = row['formnum']
        subword = row['subword']
        pos = row['pos']
        inner = row['inner']
        if not inner:
            if pos:
                results[formnum] += '-'
            results[formnum] = results.get(formnum, "") + row['subword']
        else:
            results[formnum] = results[formnum][:pos] + '(' + subword + ')' + results[formnum][pos:]
    return results
