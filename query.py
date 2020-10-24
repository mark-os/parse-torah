import sqlite3
import sys

conn = sqlite3.connect('bible.db')

conn.row_factory = sqlite3.Row
query = sys.argv[1]
print('querying '+ query)
results = {}
for row in conn.execute("""
    select w.word as baseword, formnum, pos, inner, w2.word as subword
    from formations f
    join words w on w.ord = f.baseword
    join words w2 on w2.ord = f.subword
    where w.word = ?
""",(query,)):
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
print("\n".join(results.values()))

conn.close()
