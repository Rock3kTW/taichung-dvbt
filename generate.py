import requests
import datetime
from lxml import etree

# 來源：twdvbt_xmltv 的 data.json（台灣無線台頻道 + EPG URL）
DATA_URL = "https://raw.githubusercontent.com/wenchen/twdvbt_xmltv/master/data.json"

# 抓頻道資料
channels_data = requests.get(DATA_URL).json()

# 建立 XMLTV 主體
tv = etree.Element("tv", attrib={"generator-info-name": "Taiwan-DVBT-Taichung"})

# 建立 <channel> 區塊
for ch in channels_data:
    ch_node = etree.SubElement(tv, "channel", id=ch["id"])
    etree.SubElement(ch_node, "display-name").text = ch["name"]

# 抓 7 天節目表
today = datetime.date.today()
days = 7

for ch in channels_data:
    epg_url = ch["guide"]
    for i in range(days):
        date = today + datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        url = epg_url.replace("{date}", date_str)
        print("Fetching:", url)

        try:
            data = requests.get(url, timeout=10).json()
        except:
            continue

        if "programs" not in data:
            continue

        for p in data["programs"]:
            start = p["start"].replace("-", "").replace(":", "").replace(" ", "") + " +0800"
            end = p["end"].replace("-", "").replace(":", "").replace(" ", "") + " +0800"

            prog = etree.SubElement(tv, "programme", start=start, stop=end, channel=ch["id"])

            title = etree.SubElement(prog, "title", lang="zh-TW")
            title.text = p.get("title", "無節目名稱")

            desc = etree.SubElement(prog, "desc", lang="zh-TW")
            desc.text = p.get("desc", "無節目描述")

# 輸出 XMLTV
xml = etree.tostring(tv, encoding="utf-8", pretty_print=True, xml_declaration=True)

with open("taichung-dvbt.xml", "wb") as f:
    f.write(xml)

print("EPG generated: taichung-dvbt.xml")
