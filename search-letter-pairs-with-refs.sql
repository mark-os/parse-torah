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
),
resh_refs AS (
    SELECT r.original_word, r.new_word,
           GROUP_CONCAT(DISTINCT b1.title || ' ' || v1.chapter || ':' || v1.verse) as resh_verses,
           l1.def as def_resh
    FROM replacements r
    JOIN words w1 ON w1.word = r.original_word
    JOIN verses v1 ON v1.word = w1.wordid
    JOIN books b1 ON v1.book = b1.ord
    LEFT JOIN lexicon l1 ON v1.idx = l1.idx
    GROUP BY r.original_word, r.new_word, l1.def
),
tav_refs AS (
    SELECT r.original_word, r.new_word,
           GROUP_CONCAT(DISTINCT b2.title || ' ' || v2.chapter || ':' || v2.verse) as tav_verses,
           l2.def as def_tav
    FROM replacements r
    JOIN words w2 ON w2.word = r.new_word
    JOIN verses v2 ON v2.word = w2.wordid
    JOIN books b2 ON v2.book = b2.ord
    LEFT JOIN lexicon l2 ON v2.idx = l2.idx
    GROUP BY r.original_word, r.new_word, l2.def
)
SELECT 
    rr.original_word as word_with_resh,
    rr.new_word as word_with_tav,
    rr.def_resh,
    tr.def_tav,
    rr.resh_verses as verses_with_resh,
    tr.tav_verses as verses_with_tav
FROM resh_refs rr
JOIN tav_refs tr ON rr.original_word = tr.original_word 
    AND rr.new_word = tr.new_word
ORDER BY rr.original_word;
