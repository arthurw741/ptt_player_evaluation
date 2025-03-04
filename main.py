
### 直接暴力法，把全部抓下來直接做切分
from langchain_openai import OpenAIEmbeddings

# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma         # ChromaDB 向量資料庫
from langchain.docstore.document import Document             # LangChain 文件物件
from langchain.text_splitter import RecursiveCharacterTextSplitter  # 文本切分器
import json
from dotenv import dotenv_values
from pprint import pprint

api_key=dotenv_values('.env')["API_KEY"]

print(api_key)

with open("ptt_baseball_articles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

data = data[:2]
# 將每篇文章轉換為 LangChain Document 物件，並將留言(pushes)內容合併到文章中
documents = []
for article in data:
    # 將每則留言的 content 取出，移除前導冒號與多餘空白，並合併成一個字串
    pushes_text = "\n".join([push["content"].lstrip(": ").strip() for push in article.get("pushes", [])])
    # 合併文章正文與留言內容，並以「留言內容：」作為區隔
    full_text = article["content"].strip() + "\n\n留言內容：\n" + pushes_text
    # 將 URL 與作者資訊存入 metadata，以便後續追蹤來源
    metadata = {"url": article["url"], "author_id": article["author_id"]}
    documents.append(Document(page_content=full_text, metadata=metadata))

# pprint(documents)

# 使用 RecursiveCharacterTextSplitter 將長文本切分成較小的區塊，
# 避免單一文件過長而超出模型上下文長度限制 (此處設定每塊約 1000 字，重疊 200 字)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

print("共切分出文件數量:", len(docs))

# 初始化 OpenAI 的嵌入模型 (請將 "YOUR_OPENAI_API_KEY" 替換為你的 API 金鑰)
embeddings = OpenAIEmbeddings(openai_api_key=api_key)

# print(embeddings)

# 利用 Chroma 建立向量資料庫，並將切分後的文件進行向量化存入資料庫
# collection_name 可用於區分不同的資料集，此處命名為 "ptt_baseball"
vectorstore = Chroma.from_documents(docs, embeddings, collection_name="ptt_baseball")

print(vectorstore._collection.count())

# 測試查詢：根據使用者輸入的查詢文字，從向量資料庫中檢索最相關的文章片段
query = "王念好"
retrieved_docs = vectorstore.similarity_search(query, k=1)

print(len(retrieved_docs))

# 輸出檢索結果：印出每個結果的文章 URL 與部分內容摘要 (前 200 字)
for doc in retrieved_docs:
    print("文章 URL:", doc.metadata.get("url"))
    print("內容摘要:", doc.page_content[:200])
    print("=" * 50)