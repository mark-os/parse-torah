# Done: Parses through XML of the Torah, stripping vowels/accents and loading
#       data into a Sqlite DB
# To do: Generate permutations of words based on other words found in the Torah
#        Match up words to KJV and Strong's numbers
#        Regenerate the torah as an interlinear bible in wiki friendly format
# To run this script, first unzip Tanach.xml.zip
# Source of the zip: https://www.tanach.us/Books/Tanach.xml.zip

import sqlite3
import xml.etree.ElementTree as ET
from itertools import combinations

# conn = sqlite3.connect('bible.db')
conn = sqlite3.connect(':memory:')

cursor = conn.cursor()
cursor.execute('PRAGMA foreign_keys = ON;')
conn.commit()

# Create tables
cursor.execute('''
CREATE TABLE books(
    ord     INTEGER PRIMARY KEY, 
    title   TEXT UNIQUE
    );
''')

cursor.execute('''
CREATE TABLE words(
    ord     INTEGER PRIMARY KEY, 
    word    TEXT UNIQUE
    );
''')

cursor.execute('''
CREATE TABLE verses(
    book    INTEGER,
    chapter INTEGER,
    verse   INTEGER,
    wordnum INTEGER,
    word    INTEGER,
    PRIMARY KEY(book,chapter,verse,wordnum),
    FOREIGN KEY(word) REFERENCES words(ord),
    FOREIGN KEY(book) REFERENCES books(ord)

    );
''')

conn.commit()

letters = 'אבגדהוזחטיךכלםמןנסעףפץצקרשת'

wordset = set()

book = ET.parse('Books/Genesis.xml')
bookname = book.find('tanach/book/names/name').text
cursor.execute('INSERT INTO books (title) VALUES(?);', (bookname,))
booknum = cursor.lastrowid
root = book.find('tanach/book')
for chapter in root.iter('c'):
    chapnum = chapter.get('n')
    for v in chapter.iter('v'):
        vnum = v.get('n')
        for i, w in enumerate(v.iter('w'), start=1):
            word = ''.join(c for c in w.text if c in letters)
            if word in wordset:
                cursor.execute('SELECT ord FROM words WHERE word = ?;', (word,))
                order = cursor.fetchone()[0]
            else:
                wordset.add(word)
                cursor.execute('INSERT INTO words (word) VALUES(?);', (word,))
                order = cursor.lastrowid
            cursor.execute(
                'INSERT INTO verses (book,chapter,verse,wordnum,word) VALUES(?,?,?,?,?)',
                (booknum, chapnum, vnum, i, order)
            )
            print('c' + chapnum + 'v' + vnum + 'w' + str(i) + ': ' + word + ' , ' + str(order))
        conn.commit()

for word in wordset:
    substrings = []
    for x, y in combinations(range(len(word) + 1), r = 2):
        if y-x != len(word) and word[x:y] in wordset:
            substrings.append(word[x:y])
    if len(substrings) > 0:
        print (word + ': ' + str(substrings)) 

db_file = sqlite3.connect('bible.db')
conn.backup(db_file)

conn.close()