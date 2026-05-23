import requests
from datetime import datetime, timedelta
from lxml import etree

CHANNELS = {
    "PTS": "https://epg.pw/xmltv/PTS.xml",
    "PTS2": "https://epg.pw/xmltv/PTS2.xml",
    "PTS3": "https://epg.pw/xmltv/PTS3.xml",
    "TTV": "https://epg.pw/xmltv/TTV.xml",
    "TTVNEWS": "https://epg.pw/xmltv/TTVNEWS.xml",
    "CTV": "https://epg.pw/xmltv/CTV.xml",
    "CTVNEWS": "https://epg.pw/xmltv/CTVNEWS.xml",
    "CTS": "https://epg.pw/xmltv/CTS.xml",
    "CTSNEWS": "https://epg.pw/xmltv/CTSNEWS.xml",
    "FTV": "https://epg.pw/xmltv/FTV.xml",
    "FTVNEWS": "https://epg.pw/xmltv/FTVNEWS.xml",
    "HAKKA": "https://epg.pw/xmltv/HAKKA.xml",
    "TITV": "https://epg.pw/xmltv/TITV.xml"
}

def fetch_xml(url):
    print(f"Downloading: {url}")
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return etree.fromstring(resp.content)

def convert_time(utc_str):
    fmt = "%Y%m%dT%H%M%SZ"
    dt = datetime.strptime(utc_str, fmt)
    dt += timedelta(hours=8)
    return dt.strftime("%Y%m%dT%H%M%S +0800")

print("Building Taiwan EPG (UTC+8)...")

tv = etree.Element("tv", attrib={"generator-info-name": "epg.pw multi-channel + UTC+8"})

for name, url in CHANNELS.items():
    try:
        xml = fetch_xml(url)

        # 複製 <channel>
        for ch in xml.findall("channel"):
            tv.append(ch)

        # 複製 <programme>
        for prog in xml.findall("programme"):
            start = convert_time(prog.get("start"))
            stop = convert_time(prog.get("stop"))

            new_prog = etree.SubElement(
                tv,
                "programme",
                start=start,
                stop=stop,
                channel=prog.get("channel")
            )

            # 保留完整節目描述（D1）
            for child in prog:
                new_prog.append(child)

    except Exception as e:
        print(f"Error processing {name}: {e}")

# 輸出 XMLTV
xml_bytes = etree.tostring(tv, encoding="utf-8", pretty_print=True, xml_declaration=True)

with open("docs/epg.xml", "wb") as f:
    f.write(xml_bytes)

print("EPG generated successfully: docs/epg.xml")
