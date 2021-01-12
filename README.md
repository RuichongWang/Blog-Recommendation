# Blog Recommendation
This project builds a medical blog recommendation system that connects to MongoDB Database based on the information extracted by TF-IDF algorithm. As a result, website’s Daily Active Users (DAU) increased by 13%. 
## Repository contents
### python Fit.py
This file uses pymongo and can automatically read all the blogs stored in MongoDB every two days. Then, it will output two similarity matrixes which are calculated by TF-IDF Algorithm on blog content and blog abstract. 
### Recommend.py
```
python Recommend.py passage_id
```
This requires passage_id as an input, it loads the similarity matrixes calculated by Fit.py and outputs the top N similar blogs' ID.
