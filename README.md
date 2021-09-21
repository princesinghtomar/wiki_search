# Mini Project

## Wikipedia Search Engine

>   Prince Singh Tomar

### Files : 
-   indexer.py :
    -   Contains Code For parsing wiki dump & creating smaller files that can be merged later.
-   Search.py :
    -   Contains the main code for searching including ranking system,top 10 search results will be stored in queries_op.txt.
-   merge.py :
    -   Contains the code for merging the index file and splitting it file so as to make it fast during search process.

### Usage :
-   indexer.py :
    -   python3 `indexer.py` <location_of_dump> ../inverted_indexes/wii stat_file.txt
-   merge.py :
    -   python3 `merge.py`
-   search.py :
    -   python3 `search.py` ../inverted_indexes/wii <location_of_queries_file>
