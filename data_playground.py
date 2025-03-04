import json
import pandas as pd
from pprint import pprint
# import matplotlib.pyplot as plt

# 讀取 JSON 檔案 (假設檔名為 ptt_baseball_articles.json)
with open('ptt_baseball_articles.json', 'r', encoding='utf-8') as f:
    articles = json.load(f)

# 建立 DataFrame，每一筆資料代表一篇文章
df = pd.DataFrame(articles)

# print(articles)

# print(df)
print(articles[0]['content'])
print(articles[0]['pushes'][0]['content'])