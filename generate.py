import requests
import datetime
from lxml import etree

# 台中 DVB-T 23 台頻道對照表
channels = [
    ("tw.pts", "公視 PTS HD", "PTS"),
    ("tw.ptstaigi", "公視台語台", "PTSTAIGI"),
    ("tw.pts2", "公視2台", "PTS2"),
    ("tw.pts3", "公視3台", "PTS3"),
    ("tw.ptsplus", "公視+ 教育文化", "PTSPLUS"),

    ("tw.ttv", "台視 HD", "TTV"),
    ("tw.ttvnews", "台視新聞台", "TTVNEWS"),
    ("tw.ttvfinance", "台視財經台", "TTVFIN"),

    ("tw.ctv", "中視 HD", "CTV"),
    ("tw.ctvnews", "中視新聞台", "CTVNEWS"),
    ("tw.ctvclassic", "中視經典台", "CTVCLASSIC"),

    ("tw.cts", "華視 HD", "CTS"),
    ("tw.ctsnews", "華視新聞資訊台", "CTSNEWS"),
    ("tw.ctsedu", "華視教育文化台", "CTSEDU"),

    ("tw.ftv", "民視 HD", "FTV"),
    ("tw.ftvnews", "民視新聞台", "FTVNEWS"),
    ("tw.ftv1", "民視第一台", "FTV1"),
    ("tw.ftvtaiwan", "民視台灣台", "FTVTAIWAN"),

    ("tw.hakka", "客家電視台", "HAKKA"),
    ("tw.hakka2", "客家電視2台", "HAKKA2"),

    ("tw.titv", "原住民族電視台 TITV", "TITV"),
    ("tw.titv2", "原民生活台 TITV2", "TITV2"),

    ("tw.moe", "學習頻道", "MOE")
]

# EPG 來源（穩定、合法）
EPG_SOURCE = "https://epg-api.tv.tw/epg/{channel}/{date}.json"

# 建立 XMLTV 主體
tv = etree.Element("tv", attrib={"generator-info-name": "Taiwan-DVBT-Taichung"})

# 建立 <channel> 區塊
for cid, cname, _ in channels:
    ch = etree.SubElement(tv, "channel", id=cid)
    etree.SubElement(ch, "display-name").text = cname

# 抓取 7 天節目表
today = datetime.date.today()
days = 7

for cid, cname, epg_id in channels:
    for i in range(days):
        date = today + datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        url = EPG_SOURCE.format(channel=epg_id, date=date_str)
        print("Fetching:", url)

        try:
            data = requests.get(url, timeout=10).json()
        except:
            continue

        if "programs" not in data:
            continue

        for p in data["programs"]:
            start = p["startTime"].replace("-", "").replace(":", "").replace(" ", "") + " +0800"
            end = p["endTime"].replace("-", "").replace(":", "").replace(" ", "") + " +0800"

            prog = etree.SubElement(tv, "programme", start=start, stop=end, channel=cid)

            title = etree.SubElement(prog, "title", lang="zh-TW")
            title.text = p.get("name", "無節目名稱")

            desc = etree.SubElement(prog, "desc", lang="zh-TW")
            desc.text = p.get("description", "無節目描述")

# 輸出 XMLTV
xml = etree.tostring(tv, encoding="utf-8", pretty_print=True, xml_declaration=True)

with open("taichung-dvbt.xml", "wb") as f:
    f.write(xml)

print("EPG generated: taichung-dvbt.xml")

