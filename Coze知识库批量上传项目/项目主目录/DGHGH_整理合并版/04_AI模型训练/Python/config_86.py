import requests, json

# 替换成你的 Coze 个人访问令牌（在个人设置 – API 访问令牌中创建）
TOKEN = "your_personal_access_token"
# 填入你要导出的所有插件的 ID
PLUGIN_IDS = ["plugin_id_1", "plugin_id_2"]

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

all_data = {}

for pid in PLUGIN_IDS:
    r = requests.get(f"https://api.coze.cn/v1/plugins/{pid}", headers=headers)
    if r.status_code == 200:
        all_data[pid] = r.json()
        print(f"插件 {pid} 获取成功")
    else:
        print(f"插件 {pid} 失败，状态码 {r.status_code}，信息：{r.text}")

with open("plugins_full_dump.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print("全部插件信息已保存至 plugins_full_dump.json")