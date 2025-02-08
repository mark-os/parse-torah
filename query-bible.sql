-- SQLite Queries for Biblical Hebrew Database

-- Basic verse lookup
SELECT b.title, v.chapter, v.verse, w.word, v.astrong, l.xlit, l.def
FROM verses v
JOIN books b ON v.book = b.ord
JOIN words w ON v.word = w.ord
LEFT JOIN lexicon l ON v.idx = l.idx
WHERE b.title = 'Genesis' 
AND v.chapter = 1 
AND v.verse = 1
ORDER BY v.ord;

-- Find all occurrences of a specific Hebrew word
SELECT b.title, v.chapter, v.verse, w.word, l.def
FROM verses v
JOIN books b ON v.book = b.ord
JOIN words w ON v.word = w.ord
LEFT JOIN lexicon l ON v.idx = l.idx
WHERE w.word = 'בראשית'
ORDER BY b.ord, v.chapter, v.verse;

-- Look up word formations (compound words)
SELECT w1.word as complete_word, 
       w2.word as subword,
       f.pos as position,
       f.inner as is_inner
FROM formations f
JOIN words w1 ON f.baseword = w1.ord
JOIN words w2 ON f.subword = w2.ord
WHERE w1.word = 'בראשית'
ORDER BY f.formnum, f.pos;

-- Find words by Strong's number
SELECT DISTINCT w.word, l.xlit, l.def, l.pos
FROM verses v
JOIN words w ON v.word = w.ord
JOIN lexicon l ON v.idx = l.idx
WHERE l.strong = 'H7225'
ORDER BY w.word;

-- Count word frequency
SELECT w.word, COUNT(*) as frequency
FROM verses v
JOIN words w ON v.word = w.ord
GROUP BY w.word
ORDER BY frequency DESC
LIMIT 20;

-- Find verses containing specific root letters
SELECT b.title, v.chapter, v.verse, w.word
FROM verses v
JOIN books b ON v.book = b.ord
JOIN words w ON v.word = w.ord
WHERE w.word LIKE '%ברא%'
ORDER BY b.ord, v.chapter, v.verse;
