-- Find pairs of words where ר is replaced with ת (single replacement only)
WITH RECURSIVE
chars(str, pos) AS (
  SELECT word, 1 
  FROM words 
  WHERE word LIKE '%ר%'
  UNION ALL
  SELECT str, pos+1 
  FROM chars 
  WHERE pos < length(str)
),
replacements(original_word, new_word) AS (
  SELECT str as original_word,
         substr(str, 1, pos-1) || 'ת' || substr(str, pos+1) as new_word
  FROM chars
  WHERE substr(str, pos, 1) = 'ר'
)
SELECT 
    r.original_word as word_with_resh,
    r.new_word as word_with_tav,
    l1.def as def_resh,
    l2.def as def_tav
FROM replacements r
JOIN words w2 ON w2.word = r.new_word
JOIN verses v1 ON v1.word = (SELECT wordid FROM words WHERE word = r.original_word)
JOIN verses v2 ON v2.word = w2.wordid
LEFT JOIN lexicon l1 ON v1.idx = l1.idx
LEFT JOIN lexicon l2 ON v2.idx = l2.idx
WHERE r.new_word IN (SELECT word FROM words)
GROUP BY r.original_word, r.new_word
ORDER BY r.original_word;
