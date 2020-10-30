# Done: Parses through XML of the Torah, stripping vowels/accents and loading
#       data into a Sqlite DB, also inserting formations
# To do: Match up words to KJV and Strong's numbers
#        Regenerate the torah as an interlinear bible in wiki friendly format
# To run this script, first unzip Tanach.xml.zip (included)
# Source of the zip: https://www.tanach.us/Books/Tanach.xml.zip

import sqlite3
import xml.etree.ElementTree as ET
from itertools import product
from more_itertools import partitions

# conn = sqlite3.connect('bible.db')
conn = sqlite3.connect(':memory:')

conn.execute('PRAGMA foreign_keys = ON;')
conn.commit()

# Create tables
conn.execute('''
CREATE TABLE books(
    ord     INTEGER PRIMARY KEY, 
    title   TEXT UNIQUE COLLATE NOCASE
    );
''')

conn.execute('''
CREATE TABLE words(
    ord      INTEGER PRIMARY KEY, 
    word     TEXT UNIQUE,
    gematria INTEGER,
    base7    INTEGER
    );
''')

conn.execute('''
CREATE TABLE verses(
    book    INTEGER,
    chapter INTEGER,
    verse   INTEGER,
    ord     INTEGER,
    word    INTEGER,
    PRIMARY KEY(book,chapter,verse,ord),
    FOREIGN KEY(word) REFERENCES words(ord),
    FOREIGN KEY(book) REFERENCES books(ord)
    ) WITHOUT ROWID;
''')

conn.execute('''
CREATE TABLE formations(
    baseword    INTEGER,
    formnum     INTEGER,
    pos         INTEGER,
    inner       BOOLEAN,
    subword     INTEGER,
    PRIMARY KEY(baseword,formnum,pos),
    FOREIGN KEY(baseword) REFERENCES words(ord),
    FOREIGN KEY(subword) REFERENCES words(ord)
    ) WITHOUT ROWID;
''')

conn.commit()

letters = 'אבגדהוזחטיךכלםמןנסעףפץצקרשת'

worddict = {}


booklist = [
    'Genesis',
    'Exodus',
    'Leviticus',
    'Numbers',
    'Deuteronomy',
    'Joshua',
    'Judges',
    'Ruth',
    'Samuel_1',
    'Samuel_2',
    'Kings_1',
    'Kings_2',
    'Chronicles_1',
    'Chronicles_2',
    'Ezra',
    'Nehemiah',
    'Esther',
    'Job',
    'Psalms',
    'Proverbs',
    'Ecclesiastes',
    'Song_of_Songs',
    'Isaiah',
    'Jeremiah',
    'Lamentations',
    'Ezekiel',
    'Daniel',
    'Hosea',
    'Joel',
    'Amos',
    'Obadiah',
    'Jonah',
    'Micah',
    'Nahum',
    'Habakkuk',
    'Zephaniah',
    'Haggai',
    'Zechariah',
    'Malachi'
]

def parse_book(filename):
    book = ET.parse(filename)
    bookname = book.find('tanach/book/names/name').text
    booknum = conn.execute('INSERT INTO books (title) VALUES(?);', (bookname,)).lastrowid
    root = book.find('tanach/book')

    # Iterate through XML and get chapter/verse numbers as well as word order
    for chapter in root.iter('c'):
        chapnum = chapter.get('n')
        # print(f'parsing {bookname} chapter {chapnum}')
        for verse in chapter.iter('v'):
            vnum = verse.get('n')
            for index, w in enumerate(verse.iter('w'), start=1):
                # strip out diacritic characters
                word = ''.join(c for c in w.text if c in letters)
                insert_word(booknum, chapnum, vnum, word, index)
        # conn.commit()

def insert_word(book, chapter, verse, word, order):
    # calculate gematria with mod 9 arithmetic
    total = sum([letters.index(l) + 1 for l in word])
    gematria =  total % 9 or 9
    # base 7 gematria
    base7 = total % 7 or 7
    if (wordnum := worddict.get(word)):
        pass
    else:
        wordnum = conn.execute('INSERT INTO words (word,gematria,base7) VALUES(?,?,?);', (word,gematria,base7)).lastrowid
        worddict[word] = wordnum
    
    conn.execute(
        'INSERT INTO verses (book,chapter,verse,ord,word) VALUES(?,?,?,?,?)',
        (book, chapter, verse, order, wordnum)
    )


def parse_partition(part): # array of subarrays of characters
    result = []
    pos = 0
    for sub in part:
        w = "".join(sub) # subarray to string
        sub_wordnum = worddict.get(w)
        if not sub_wordnum: # this should be a word, if not, the parition is no good
            return
        result.append((sub_wordnum, pos, False)) # Not an inner word
        pos += len(w)
    return result

def parse_inside(part): # array of 3
    result = []
    first = "".join(part[0])
    last = "".join(part[2])
    outer = first + last
    outer_num = worddict.get(outer)
    if not outer_num:
        return
    inner = "".join(part[1])
    inner_num = worddict.get(inner)
    if not inner_num:
        return
    result = [(outer_num,0,False),(inner_num,len(first),True)]
    return result

def insert_formation(wordnum, result):
    formnum = conn.execute(
        'SELECT MAX(formnum) FROM formations WHERE baseword = ?',(wordnum,)
    ).fetchone()[0] or 0
    formnum += 1
    conn.executemany(
        'INSERT INTO formations (baseword,formnum,pos,inner,subword) VALUES (?,?,?,?,?)',
        [(wordnum, formnum, pos, inside, sub_wordnum) for sub_wordnum, pos, inside in result]
    )


# Populate "Book 0" with 1,2,3 letter permutations

conn.execute("INSERT INTO books (ord,title) VALUES(0,'Book0');")

index = 0
for letter in letters:
    index += 1
    insert_word(0,1,index,letter,1)
index = 0
for a,b in product(letters, repeat=2): # These 2-letter combinations are called "gates"
    index += 1
    insert_word(0,2,index,a+b,1)
index = 0
for a,b,c in product(letters, repeat=3): # These 3-letter combinations are called "roots"
    index += 1
    insert_word(0,3,index,a+b+c,1)


# Parse all books of the Tanach, insert all words/verses

for book in booklist:
    parse_book(f'Books/{book}.xml')


# Populate formations table

for word,wordnum in worddict.items():
    for part in partitions(word):
        if len(part) != 1:
            result = parse_partition(part)
            if result: insert_formation(wordnum, result)
        if len(part) == 3:
            result = parse_inside(part)
            if result: insert_formation(wordnum, result)


# Save the in-memory DB to a file
conn.commit()

db_file = sqlite3.connect('bible.db')
conn.backup(db_file)

conn.close()