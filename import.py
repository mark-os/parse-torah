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
    ord      INTEGER PRIMARY KEY, 
    word     TEXT UNIQUE,
    gematria INTEGER
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
    FOREIGN KEY(word) REFERENCES words(ord),
    FOREIGN KEY(book) REFERENCES books(ord)
    );
''')

cursor.execute('''
CREATE TABLE formations(

    );
''')

conn.commit()

letters = 'אבגדהוזחטיךכלםמןנסעףפץצקרשת'

# TODO: Populate words with 1,2,3 letter combinations

wordset = set()

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
                word = ''.join(c for c in w.text if c in letters)
                insert_word(booknum, chapnum, vnum, word, index)
        conn.commit()

def insert_word(book, chapter, verse, word, order):
    if word in wordset:
        cursor.execute('SELECT ord FROM words WHERE word = ?;', (word,))
        wordnum = cursor.fetchone()[0]
    else:
        wordset.add(word)
        cursor.execute('INSERT INTO words (word) VALUES(?);', (word,))
        wordnum = cursor.lastrowid
    cursor.execute(
        'INSERT INTO verses (book,chapter,verse,ord,word) VALUES(?,?,?,?,?)',
        (book, chapter, verse, order, wordnum)
    )

for book in booklist:
    parse_book(f'Books/{book}.xml')


db_file = sqlite3.connect('bible.db')
conn.backup(db_file)

conn.close()