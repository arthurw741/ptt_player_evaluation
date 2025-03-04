from openai import OpenAI
from dotenv import dotenv_values
from pprint import pprint

client = OpenAI(
  api_key=dotenv_values('.env')["API_KEY"]
)

def openai_api(content: str):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", 
            "content": content}
            ],
        max_tokens=50,                 # 設定生成回應中最多可包含的 token 數量
        temperature=0.1,               # 採樣溫度，控制生成結果的隨機性（較高值會使結果更具多樣性）
        top_p=1,                       # nucleus sampling 的累積機率閥值，用於控制生成文本的多樣性
        n=1,                           # 指定生成回應的數量，常用於需要多個備選回應時
        stream=False,                  # 是否以流式傳輸的方式返回生成內容（True 時可實時獲取生成進度）
        stop=["\n"],                   # 停止序列列表，當生成內容遇到這些序列時會提前終止
        presence_penalty=0,            # 主題出現懲罰，控制模型引入新主題的傾向（範圍通常在 -2.0 到 2.0 之間）
        frequency_penalty=0,           # 頻率懲罰，用於降低模型重複相同 token 的可能性（範圍通常在 -2.0 到 2.0 之間）
        logit_bias={},                 # 調整特定 token 生成概率的字典（格式為 {token_id: bias}，用於微調生成內容）
        # user="user-identifier",        # 用戶標識符，用於追蹤 API 調用與防止濫用
    )
    response = completion.choices[0].message.content
    return response

content = "棒球選手陳傑憲的評價如何?"
res = openai_api(content=content)
print(res)
# pprint(completion)
