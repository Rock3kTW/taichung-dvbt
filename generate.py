import requests
import datetime
from lxml import etree

# 台中 DVB-T → MOD EPG 對照表
CHANNEL_MAP = {
    "tw.pts": "PTS-HD",
    "tw.ptstaigi": "PTS-TAIGI",
    "tw.pts2": "PTS2",
    "tw.pts3": "PTS3",
    "tw.ptsplus": "PTS-PLUS",
    "tw.ttv": "TTV-HD",
    "tw.ttvnews": "TTV-NEWS",
    "tw.ttvfinance": "TTV-FINANCE",
    "tw.ctv": "CTV-HD",
    "tw.ctvnews": "CTV-NEWS",
    "tw.ctvclassic": "CTV-CLASSIC",
    "tw.cts": "CTS-HD",
    "tw.ctsnews": "CTS-NEWS",
    "tw.ctsedu": "CTS-EDU",
    "tw.ftv": "FTV-HD",
    "tw.ftvnews": "FTV-NEWS",
    "tw.ftv1": "FTV-ONE",
    "tw.ftvtaiwan": "FTV-TAIWAN",
    "tw.hakka": "HAKKA-TV",
    "tw.hakka2": "HAKKA2",
    "tw.titv": "TITV",
    "tw.titv2": "TITV2",
    "tw.moe": "MOE-CHANNEL"
}

# MOD 官方 EPG API
EPG_URL = "https://epg-api.video.friday.tw/v1/channel/{mod_id}/{date}.json"

# 建立 XMLTV 主體
tv = etree.Element("tv", attrib={"generator-info-name": "Taiwan-DVBT-Taichung"})

# 建立 <channel>
for cid in CHANNEL_MAP:
    ch = etree.SubElement(tv, "channel", id=cid)
    etree.SubElement(ch, "display-name").text = cid

# 抓 7 天節目
today = datetime.date.today()

for cid, mod_id in CHANNEL_MAP.items():
    for i in range(7):
        date = today + datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        url = EPG_URL.format(mod_id=mod_id, date=date_str)
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

            prog = etree.SubElement(tv, "programme", start=start, stop=end, channel=cid)

            title = etree.SubElement(prog, "title", lang="zh-TW")
            title.text = p.get("title", "無節目名稱")

            desc = etree.SubElement(prog, "desc", lang="zh-TW")
            desc.text = p.get("desc", "無節目描述")

# 輸出 XMLTV
xml = etree.tostring(tv, encoding="utf-8", pretty_print=True, xml_declaration=True)

with open("taichung-dvbt.xml", "wb") as f:
    f.write(xml)

print("EPG generated: taichung-dvbt.xml")
