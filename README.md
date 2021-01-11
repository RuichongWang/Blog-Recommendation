# Blog-Recommendation

The program is designed to make blog recommendations on a blog website. 

By running Fit.py, it uses pymongo and can automatically read all the blogs stored in MongoDB every two days. Then, it will output two similarity matrixes which are calculated by TF-IDF Algorithm on blog content and blog abstract. 

By running Recommend.py, which requires passage ID as an input, it loads the similarity matrixes calculated by Fit.py and outputs the top N similar blogs' ID.
