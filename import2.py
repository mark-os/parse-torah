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
conn = sqlite3.connect(":memory:")

conn.execute("PRAGMA foreign_keys = ON;")
conn.commit()

# Create tables
conn.execute(
    """
CREATE TABLE books(
    ord     INTEGER PRIMARY KEY, 
    osis    TEXT UNIQUE COLLATE NOCASE,
    title   TEXT UNIQUE COLLATE NOCASE
    );
"""
)

conn.execute(
    """
CREATE TABLE words(
    ord      INTEGER PRIMARY KEY, 
    word     TEXT UNIQUE,
    gematria INTEGER,
    base7    INTEGER
    );
"""
)

conn.execute(
    """
CREATE TABLE lexicon(
    idx   INTEGER PRIMARY KEY,
    strong  TEXT,
    xlit    TEXT,
    pos     TEXT,
    def     TEXT
    )
"""
)

conn.execute(
    """
CREATE TABLE verses(
    book    INTEGER,
    chapter INTEGER,
    verse   INTEGER,
    ord     INTEGER,
    word    INTEGER,
    idx     INTEGER,
    --osisID  TEXT,
    --kjv     TEXT,
    astrong TEXT,
    PRIMARY KEY(book,chapter,verse,ord),
    FOREIGN KEY(word) REFERENCES words(ord),
    FOREIGN KEY(book) REFERENCES books(ord)
    FOREIGN KEY(idx) REFERENCES lexicon(idx)
    ) WITHOUT ROWID;
"""
)

conn.execute(
    """
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
"""
)


conn.commit()

letters = "אבגדהוזחטיךכלםמןנסעףפץצקרשת"

worddict = {}


booklist = {
    "Gen": "Genesis",
    "Exod": "Exodus",
    "Lev": "Leviticus",
    "Num": "Numbers",
    "Deut": "Deuteronomy",
    "Josh": "Joshua",
    "Judg": "Judges",
    "Ruth": "Ruth",
    "1Sam": "Samuel_1",
    "2Sam": "Samuel_2",
    "1Kgs": "Kings_1",
    "2Kgs": "Kings_2",
    "1Chr": "Chronicles_1",
    "2Chr": "Chronicles_2",
    "Ezra": "Ezra",
    "Neh": "Nehemiah",
    "Esth": "Esther",
    "Job": "Job",
    "Ps": "Psalms",
    "Prov": "Proverbs",
    "Eccl": "Ecclesiastes",
    "Song": "Song_of_Songs",
    "Isa": "Isaiah",
    "Jer": "Jeremiah",
    "Lam": "Lamentations",
    "Ezek": "Ezekiel",
    "Dan": "Daniel",
    "Hos": "Hosea",
    "Joel": "Joel",
    "Amos": "Amos",
    "Obad": "Obadiah",
    "Jonah": "Jonah",
    "Mic": "Micah",
    "Nah": "Nahum",
    "Hab": "Habakkuk",
    "Zeph": "Zephaniah",
    "Hag": "Haggai",
    "Zech": "Zechariah",
    "Mal": "Malachi",
}


def parse_book(filename, bookname):
    book = ET.parse(filename)
    ns = {"": "http://www.bibletechnologies.net/2003/OSIS/namespace"}
    root = book.find(".//div", ns)
    osis = root.get("osisID")
    booknum = conn.execute(
        "INSERT INTO books (osis,title) VALUES(?,?);", (osis, bookname)
    ).lastrowid
    # Iterate through XML and get chapter/verse numbers as well as word order
    for chapter in root.findall("chapter", ns):
        chapnum = chapter.get("osisID").split(".")[1]
        print(f"parsing {bookname} chapter {chapnum}")
        for verse in chapter.findall("verse", ns):
            vnum = verse.get("osisID").split(".")[2]
            for order, w in enumerate(verse.findall("w", ns), start=1):
                # strip out diacritic characters
                word = "".join(c for c in w.text if c in letters)
                astrong = w.get("lemma")
                insert_word(booknum, chapnum, vnum, word, order, astrong)
        # conn.commit()


def insert_word(book, chapter, verse, word, order, astrong=None):
    strong = None
    # augmented strong sometimes contains prefixes, strip to get the strong
    if astrong:
        strong = astrong.split("/")[-1].replace(" ", "")
    # calculate gematria with mod 9 arithmetic
    total = sum([letters.index(l) + 1 for l in word])
    gematria = total % 9 or 9
    # base 7 gematria
    base7 = total % 7 or 7
    if (wordnum := worddict.get(word)) :
        pass
    else:
        wordnum = conn.execute(
            "INSERT INTO words (word,gematria,base7) VALUES(?,?,?);",
            (word, gematria, base7),
        ).lastrowid
        worddict[word] = wordnum

    conn.execute(
        """
        INSERT INTO verses (book,chapter,verse,ord,word,astrong,idx)
        VALUES(?,?,?,?,?,?,
        (SELECT idx from lexicon where strong = ?)
        )
        """,
        (book, chapter, verse, order, wordnum, astrong, strong),
    )


def parse_partition(part):  # array of subarrays of characters
    result = []
    pos = 0
    for sub in part:
        w = "".join(sub)  # subarray to string
        sub_wordnum = worddict.get(w)
        if not sub_wordnum:  # this should be a word, if not, the parition is no good
            return
        result.append((sub_wordnum, pos, False))  # Not an inner word
        pos += len(w)
    return result


def parse_inside(part):  # array of 3
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
    result = [(outer_num, 0, False), (inner_num, len(first), True)]
    return result


def insert_formation(wordnum, result):
    formnum = (
        conn.execute(
            "SELECT MAX(formnum) FROM formations WHERE baseword = ?", (wordnum,)
        ).fetchone()[0]
        or 0
    )
    formnum += 1
    conn.executemany(
        "INSERT INTO formations (baseword,formnum,pos,inner,subword) VALUES (?,?,?,?,?)",
        [
            (wordnum, formnum, pos, inside, sub_wordnum)
            for sub_wordnum, pos, inside in result
        ],
    )


def parse_lex(entry, ns):
    xref = entry.find("xref", ns)
    strong = xref.get("strong")
    if strong:
        aug = xref.get("aug")
        if aug:
            strong += aug
        xlit = entry.find("w", ns).get("xlit")
        pos = entry.find("pos", ns).text
        defn = entry.find("def", ns).text
        conn.execute(
            "INSERT INTO lexicon (strong,xlit,pos,def) VALUES (?,?,?,?)",
            (strong, xlit, pos, defn),
        )


# Populate the lexicon

lex = ET.parse("HebrewLexicon/LexicalIndex.xml").getroot()
ns = {"": "http://openscriptures.github.com/morphhb/namespace"}
for entry in lex.iterfind("part/entry", namespaces=ns):
    parse_lex(entry, ns)

# Populate "Book 0" with 1,2,3 letter permutations

conn.execute("INSERT INTO books (ord,title) VALUES(0,'Book0');")

index = 0
for letter in letters:
    index += 1
    insert_word(0, 1, index, letter, 1)
print("inserting 2 letter words")
index = 0
for a, b in product(
    letters, repeat=2
):  # These 2-letter combinations are called "gates"
    index += 1
    insert_word(0, 2, index, a + b, 1)
print("inserting 3 letter words")
index = 0
for a, b, c in product(
    letters, repeat=3
):  # These 3-letter combinations are called "roots"
    index += 1
    insert_word(0, 3, index, a + b + c, 1)


# Parse all books of the Tanach, insert all words/verses

for book in booklist:
    parse_book(f"morphhb/wlc/{book}.xml", booklist[book])


# Populate formations table

# for word, wordnum in worddict.items():
#     for part in partitions(word):
#         if len(part) != 1:
#             result = parse_partition(part)
#             if result:
#                 insert_formation(wordnum, result)
#         if len(part) == 3:
#             result = parse_inside(part)
#             if result:
#                 insert_formation(wordnum, result)


# Save the in-memory DB to a file
conn.commit()

db_file = sqlite3.connect("bible.db")
conn.backup(db_file)

conn.close()