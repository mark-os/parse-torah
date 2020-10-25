from typing import Optional
from fastapi import FastAPI
import sqlite3

app = FastAPI()


@app.get("/")
def read_root():
    return "Test query API"

@app.get("/query/{word}")
def read_item(word: str):
    
    conn = sqlite3.connect('bible.db')

    conn.row_factory = sqlite3.Row

    results = {}
    for row in conn.execute("""
        select w.word as baseword, formnum, pos, inner, w2.word as subword
        from formations f
        join words w on w.ord = f.baseword
        join words w2 on w2.ord = f.subword
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
    conn.close()
    return results