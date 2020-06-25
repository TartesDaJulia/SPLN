# Web Scraper to create an Ontology

Chose https://www.lexico.pt/, an online Portuguese dictionary.
 
- [x] Scrape https://www.lexico.pt/
- [x] Get word, meanings, synonyms, antonyms
- [x] Use words gotten to scrape the site for them.
- [x] Create ontology
    - [x] Create classes
    - [x] Create object properties isSynonym, isAntonym etc...
    - [x] Create individuals from the words scraped
    - [x] Populate
- [x] Fixes:
    - [x] Treat wordTypes
    - [x] Save synonyms and antonyms
    - [x] Correct meanings sturcture
    - [x] Make list iterate meanings corerctly
    - [ ] Got error: maximum recursion depth exceeded while calling a Python object, need to convert getWord to a loop
- [ ] Future Work:
    - [ ] Make words that point to others in the website, do so in the ontology