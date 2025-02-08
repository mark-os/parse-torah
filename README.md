# Bible Dictionary Project

This project creates a specialized SQLite database for studying the Hebrew Bible (Tanach). It's designed to be a companion tool for studying sensus plenior (the deeper meaning of Scripture) and supports the work at 2nd Book ([here](https://2ndbook.org/wiki/Main_Page) and [here](https://sensusplenior.net/wiki/Main_Page)).

You will notice in the import script we are stripping the niqqud (vowel markings) and other diacritics. That is because we are focused on studying the Hebrew text as it was originally written by God. The niqqud were added centuries after Christ (The Dead Sea Scrolls for instance do not contain those markings).

## Current Status
This is the first phase of a larger project. Currently, we are:
1. Parsing the Tanach into a searchable database
2. Incorporating Strong's numbers and lemmas for word reference
3. Importing dictionary definitions from the Hebrew Lexicon provided by the OpenScriptures project

## Prerequisites
- Python 3.x
- Git (for cloning with submodules)

## Setup
1. Clone the repository with submodules:
   ```bash
   git clone --recursive [repository-url]
   ```
   
   Or if already cloned:
   ```bash
   git submodule update --init --recursive
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
To generate the database:
```bash
make
```

This will:
1. Create a new bible.db file
2. Parse the Hebrew Bible text
3. Import lexical reference data
4. Generate the complete database

Additional make commands:

```bash
make clean     # Remove the bible.db file
make rebuild   # Clean and regenrate the database
```

## Search Capabilities
The project provides several ways to study the Hebrew text:

### REST API
There is a FastAPI server that provides word formation searches:

1. Start the API server:
```bash
uvicorn main:app --reload
```

2. Access the API:
- Test endpoint: http://localhost:8000/
- Word formation search: http://localhost:8000/query/{hebrew_word}

### SQL Examples

Example queries are provided in:
- query-bible.sql - Basic search examples
- search-letter-pairs.sql - Find word relationships through letter substitutions
- search-letter-pairs-with-refs.sql - Same as above but includes verse references

To run the example queries:
```bash
sqlite3 bible.db < query-bible.sql
```

## Project Roadmap
Future development will include:
1. Enhanced search tools for word relationships
2. Cross-referencing capabilities
3. Tools for discovering hidden meanings (sensus plenior)
4. Integration with Bible study workflows
5. Additional features to support the 2nd Book project

The goal is to make this a widely accessible tool for deeper Bible study, enabling anyone to explore the original Hebrew text and discover its hidden meanings.
