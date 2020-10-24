# Done: Parses through XML of the Torah, stripping vowels/accents and loading
#       data into a Sqlite DB
# To do: Generate formations of words based on other words
#        Match up words to KJV and Strong's numbers
#        Regenerate the torah as an interlinear bible in wiki friendly format
# To run this script, first unzip Tanach.xml.zip (included)
# Source of the zip: https://www.tanach.us/Books/Tanach.xml.zip

import sqlite3
import xml.etree.ElementTree as ET
from itertools import product
from more_itertools import partitions

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
    ord      INTEGER PRIMARY KEY, 
    word     TEXT UNIQUE,
    gematria INTEGER,
    base7    INTEGER
    );
''')

cursor.execute('''
CREATE TABLE verses(
    book    INTEGER,
    chapter INTEGER,
    verse   INTEGER,
    ord     INTEGER,
    word    INTEGER,
    PRIMARY KEY(book,chapter,verse,ord),
    FOREIGN KEY(word) REFERENCES words(ord)
    );
''')

cursor.execute('''
CREATE TABLE formations(
    baseword    INTEGER,
    formation   INTEGER,
    pos         INTEGER,
    inner       BOOLEAN,
    subword     INTEGER,
    PRIMARY KEY(baseword,formation,pos),
    FOREIGN KEY(baseword) REFERENCES words(ord),
    FOREIGN KEY(subword) REFERENCES words(ord)
    );
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
    cursor.execute('INSERT INTO books (title) VALUES(?);', (bookname,))
    booknum = cursor.lastrowid
    conn.commit()
    root = book.find('tanach/book')

    # Iterate through XML and get chapter/verse numbers as well as word order
    for chapter in root.iter('c'):
        chapnum = chapter.get('n')
        print(f'parsing {bookname} chapter {chapnum}')
        for verse in chapter.iter('v'):
            vnum = verse.get('n')
            for index, w in enumerate(verse.iter('w'), start=1):
                # strip out diacritic characters
                word = ''.join(c for c in w.text if c in letters)
                insert_word(booknum, chapnum, vnum, word, index)
        conn.commit()

def insert_word(book, chapter, verse, word, order):
    # calculate gematria with mod 9 arithmetic
    total = sum([letters.index(l) + 1 for l in word])
    gematria =  total % 9 or 9
    # base 7 gematria
    base7 = total % 7 or 7
    if (wordnum := worddict.get(word)):
        pass
    else:
        cursor.execute('INSERT INTO words (word,gematria,base7) VALUES(?,?,?);', (word,gematria,base7))
        wordnum = cursor.lastrowid
        worddict[word] = wordnum
    
    cursor.execute(
        'INSERT INTO verses (book,chapter,verse,ord,word) VALUES(?,?,?,?,?)',
        (book, chapter, verse, order, wordnum)
    )

# Populate "Book 0" with 1,2,3 letter permutations

index = 0
for letter in letters:
    index += 1
    insert_word(0,1,index,letter,1)
index = 0
for a,b in product(letters, repeat=2):
    index += 1
    insert_word(0,2,index,a+b,1)
index = 0
for a,b,c in product(letters, repeat=3):
    index += 1
    insert_word(0,3,index,a+b+c,1)
conn.commit()


# Parse all books of the Tanach, insert all words/verses

for book in booklist:
    parse_book(f'Books/{book}.xml')


# Populate formations table

def parse_partition(part, word): # array of subarrays of characters
    result = []
    for sub in part:
        w = "".join(sub) # subarray to string
        if w not in worddict: # this should be a word, if not, the parition is no good
            return
        result.append(w)
    print("  " + "-".join(result))
    return result

def parse_inside(part, word): # array of 3
    result = []
    first = "".join(part[0])
    last = "".join(part[2])
    outer = first + last
    if outer not in worddict:
        return
    inner = "".join(part[1])
    if inner not in worddict:
        return
    print("  " + first + "(" + inner + ")" + last)
    return result

# TODO: def insert_formation

count = 1
for word,ord in worddict.items():
    count += 1
    if count < 10000 or count > 10100: continue
    print(word)
    for p in partitions(word):
        if len(p) != 1: parse_partition(p, word)
        if len(p) == 3: parse_inside(p,word)
    
        
        
# Save the in-memory DB to a file

db_file = sqlite3.connect('bible.db')
conn.backup(db_file)

conn.close()