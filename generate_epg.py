import requests
import datetime
from lxml import etree

# 台中 DVB-T 無線台頻道列表
CHANNELS = {
    "tw.pts": "公視",
    "tw.ttv": "台視",
    "tw.ctv": "中視",
    "tw.cts": "華視",
    "tw.ftv": "民視",
    "tw.hakka": "客家電視台",
    "tw.titv": "原住民族電視台",
    "tw.moe": "學習頻道"
}

# 合法公開 EPG 來源（不含版權內容）
EPG_SOURCE = "https://epg.hami-plus.net/api/list/{date}/{cid}"

tv = etree.Element("tv", attrib={"generator-info-name": "Taiwan-DVBT-Taichung"})

# 建立 <channel>
for cid, name in CHANNELS.items():
    ch = etree.SubElement(tv, "channel", id=cid)
    etree.SubElement(ch, "display-name").text = name

today = datetime.date.today()

# 抓 7 天節目
for cid in CHANNELS:
    for i in range(7):
        date = today + datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        url = EPG_SOURCE.format(date=date_str, cid=cid)
        print("Fetching:", url)

        try:
            data = requests.get(url, timeout=10).json()
        except:
            continue

        if "programs" not in data:
            continue

        for p in data["programs"]:
            start = p["start"] + " +0800"
            end = p["end"] + " +0800"

            prog = etree.SubElement(tv, "programme", start=start, stop=end, channel=cid)

            title = etree.SubElement(prog, "title", lang="zh-TW")
            title.text = p.get("title", "無節目名稱")

            desc = etree.SubElement(prog, "desc", lang="zh-TW")
            desc.text = p.get("desc", "無節目描述")

# 輸出 XMLTV
xml = etree.tostring(tv, encoding="utf-8", pretty_print=True, xml_declaration=True)

with open("docs/epg.xml", "wb") as f:
    f.write(xml)

print("EPG generated: docs/epg.xml")
