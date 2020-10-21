# Done: Parses through XML of the Torah, stripping vowels/accents and loading
#       data into a Sqlite DB
# To do: Generate permutations of words based on other words found in the Torah
#        Match up words to KJV and Strong's numbers
#        Regenerate the torah as an interlinear bible in wiki friendly format
# To run this script,
# Download this file and unzip: https://www.tanach.us/Books/Tanach.xml.zip

import sqlite3
import xml.etree.ElementTree as ET

conn = sqlite3.connect('bible.db')

cursor = conn.cursor()
cursor.execute('PRAGMA foreign_keys = ON;')
conn.commit()

# Create tables
cursor.execute('''

CREATE TABLE words(
    ord     INTEGER PRIMARY KEY, 
    word    TEXT UNIQUE
    );
''')

cursor.execute('''

CREATE TABLE verses(
    book    TEXT,
    chapter INTEGER,
    verse   INTEGER,
    wordnum INTEGER,
    word    INTEGER,
    PRIMARY KEY(book,chapter,verse,wordnum)
    FOREIGN KEY(word) REFERENCES words(ord)
    );

''')
conn.commit()

letters = 'אבגדהוזחטיךכלםמןנסעףפץצקרשת'

wordset = set()

book = ET.parse('Books/Genesis.xml')
bookname = book.find('tanach/book/names/name').text
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
                # conn.commit()
                cursor.execute('SELECT ord FROM words WHERE word = ?;', (word,))
                order = cursor.fetchone()[0]
            cursor.execute(
                'INSERT INTO verses (book,chapter,verse,wordnum,word) VALUES(?,?,?,?,?)',
                (bookname, chapnum, vnum, i, order)
            )
            conn.commit()
            print('c' + chapnum + 'v' + vnum + 'w' + str(i) + ': ' + word + ' , ' + str(order))

conn.close()