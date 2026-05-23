import requests
from datetime import datetime, timedelta
from lxml import etree

SOURCE_URL = "https://epg.pw/xmltv/epg_TW.xml"

print("Downloading EPG from epg.pw...")
resp = requests.get(SOURCE_URL, timeout=20)
resp.raise_for_status()

print("Parsing XML...")
tree = etree.fromstring(resp.content)

# 建立新的 XMLTV 根節點
tv = etree.Element("tv", attrib={"generator-info-name": "epg.pw + Taiwan UTC+8 converter"})

# 複製所有 <channel>
for ch in tree.findall("channel"):
    tv.append(ch)

# 處理所有 <programme>
for prog in tree.findall("programme"):
    start = prog.get("start")  # 例如 20260523T120000Z
    stop = prog.get("stop")

    # epg.pw 使用 UTC（Z 結尾）
    fmt = "%Y%m%dT%H%M%SZ"

    try:
        start_dt = datetime.strptime(start, fmt) + timedelta(hours=8)
        stop_dt = datetime.strptime(stop, fmt) + timedelta(hours=8)
    except:
        continue

    # 建立新的 <programme>
    new_prog = etree.SubElement(
        tv,
        "programme",
        start=start_dt.strftime("%Y%m%dT%H%M%S +0800"),
        stop=stop_dt.strftime("%Y%m%dT%H%M%S +0800"),
        channel=prog.get("channel")
    )

    # 複製標題與描述
    for child in prog:
        new_prog.append(child)

# 輸出 XMLTV
xml = etree.tostring(tv, encoding="utf-8", pretty_print=True, xml_declaration=True)

with open("docs/epg.xml", "wb") as f:
    f.write(xml)

print("EPG generated: docs/epg.xml (Taiwan UTC+8)")
