.PHONY: all clean rebuild test

all: bible.db

bible.db: import2.py HebrewLexicon/LexicalIndex.xml morphhb/wlc/*.xml
	python import2.py

clean:
	rm -f bible.db

rebuild: clean all

test: bible.db
	sqlite3 bible.db < query-bible.sql

.PRECIOUS: bible.db
