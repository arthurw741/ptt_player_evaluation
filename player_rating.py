import requests
from bs4 import BeautifulSoup
import time
import json

# 建立全域 Session，並設定過18驗證 Cookie
session = requests.Session()
session.cookies.set('over18', '1')

# 設定標頭，模擬一般瀏覽器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}

def get_page(url):
    """
    傳回指定 URL 的 HTML 內容
    """
    response = session.get(url, headers=headers)
    response.encoding = 'utf-8'
    return response.text

def parse_article(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # 取得標題 (這裡我們以作者欄位代替)
    title_tag = soup.find('span', class_='article-meta-value')
    author_id = title_tag.get_text() if title_tag else '無標題'
    
    # 取得 main-content 區塊
    main_content = soup.find('div', id='main-content')
    pushes = []
    if main_content:
        # 先抓取留言推文
        push_tags = main_content.find_all('div', class_='push')
        for push in push_tags:
            tag = push.find('span', class_='push-tag').get_text(strip=True) if push.find('span', class_='push-tag') else ''
            userid = push.find('span', class_='push-userid').get_text(strip=True) if push.find('span', class_='push-userid') else ''
            push_content = push.find('span', class_='push-content').get_text(strip=True) if push.find('span', class_='push-content') else ''
            pushes.append({
                'tag': tag,
                'userid': userid,
                'content': push_content
            })
        # 移除 meta 資訊 (作者、標題、時間)
        for meta in main_content.find_all('div', class_='article-metaline'):
            meta.extract()
        for meta in main_content.find_all('div', class_='article-metaline-right'):
            meta.extract()
        # 移除留言推文區塊，避免干擾內文的提取
        for push in push_tags:
            push.extract()
        content = main_content.get_text().strip()
    else:
        content = ''
    
    return author_id, content, pushes

def main():
    base_url = 'https://www.ptt.cc'
    # 從最新的 Baseball 版首頁開始
    board_url = base_url + '/bbs/Baseball/index.html'
    
    # 依序點選「上頁」連結兩次（模擬按上一頁兩次）
    for i in range(2):
        board_html = get_page(board_url)
        board_soup = BeautifulSoup(board_html, 'html.parser')
        # 找到包含「上頁」文字的連結
        prev_link = board_soup.find('a', string='‹ 上頁')
        if prev_link:
            board_url = base_url + prev_link['href']
            print(f"進入第 {i+2} 頁: {board_url}")
        else:
            print("找不到上頁連結")
            break

    # 此時 board_url 即為點選上頁兩次後的頁面
    html = get_page(board_url)
    soup = BeautifulSoup(html, 'html.parser')
    
    # 取得當前頁所有文章連結，只爬取推文數符合條件的文章
    articles = []
    for entry in soup.select('.r-ent'):
        # 取得推文數 element (位於 .nrec)
        nrec_tag = entry.select_one('.nrec')
        if nrec_tag:
            push_count_text = nrec_tag.get_text().strip()
        else:
            push_count_text = ""
        
        # 條件：若推文數中含有 "X"，或為數字且大於20
        if ("X" in push_count_text) or (push_count_text.isdigit() and int(push_count_text) > 20):
            a_tag = entry.select_one('.title a')
            if a_tag:
                article_href = a_tag['href']
                article_url = base_url + article_href
                print(f'爬取文章：{article_url}，推文數：{push_count_text}')
                article_html = get_page(article_url)
                author_id, content, pushes = parse_article(article_html)
                articles.append({
                    'url': article_url,
                    'author_id': author_id,
                    'content': content,
                    'pushes': pushes
                })
                # 避免爬太快，延遲 0.5 秒
                time.sleep(0.5)
    
    # 將爬取結果存成 JSON 檔
    with open('ptt_baseball_articles.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print('爬取完成，資料已存檔。')

if __name__ == '__main__':
    main()
