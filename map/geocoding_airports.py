import json
import requests
import time
import re

def parse_icao_entries(raw_text):
    print("🚦 Parsing ICAO entries starting with 'EG'...")
    lines = raw_text.strip().split('\n')
    parsed = []

    for line in lines:
        match = re.search(r'\b(EG[A-Z]{2})\b', line.strip())
        if match:
            icao_code = match.group(1)
            name = line.replace(icao_code, '').strip()
            parsed.append({
                "name": name,
                "icao": icao_code
            })
        else:
            match = re.search(r'\b(EP[A-Z]{2})\b', line.strip())
            if match:
                icao_code = match.group(1)
                name = line.replace(icao_code, '').strip()
                parsed.append({
                    "name": name,
                    "icao": icao_code
                })
            else:
                print(f"❌ Skipped {line}")
    print(f"✅ Found {len(parsed)} EG ICAO entries")
    return parsed

def geocode_icao(icao):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{icao} airport",
        "format": "json",
        "limit": 1
    }
    print(f"🌍 Geocoding: {icao}")
    try:
        response = requests.get(url, params=params, headers={"User-Agent": "GeoScript/1.0"})
        data = response.json()
        if data:
            lat = data[0]["lat"]
            lon = data[0]["lon"]
            print(f"📌 {icao} = {lat}, {lon}")
            return {"latitude": float(lat), "longitude": float(lon)}
    except Exception as e:
        print(f"💥 Error geocoding {icao}: {e}")
    return None

def build_json_from_icao(raw_text):
    print("🚀 Building JSON with EG ICAO codes...")
    entries = parse_icao_entries(raw_text)
    result = []

    for entry in entries:
        print(f"🔄 Processing {entry['icao']}")
        location = geocode_icao(entry["icao"])
        result.append({
            "name": entry["name"],
            "icao": entry["icao"],
            "location": location if location else {"latitude": None, "longitude": None}
        })
        time.sleep(0.1)  # Respect Nominatim rate limits

    print("📝 Saving results...")
    try:
        with open("eg_icao_locations.json", "w", encoding="utf-8") as f:
            print("📥 Writing to file...")
            json.dump(result, f, indent=2)
    except Exception as e:
        print(f"💢 Write error: {e}")

    print(f"✅ Saved {len(result)} EG locations to eg_icao_locations.json")


raw_data = """
ABERDEEN/DYCE EGPD

ALDERNEY EGJA

ANDREWSFIELD EGSL

BARRA EGPR

BELFAST ALDERGROVE EGAA
6.
BELFAST/CITY EGAC
7.
BENBECULA EGPL
8.
BIGGIN HILL EGKB
9.
BIRMINGHAM EGBB
10.
BLACKBUSHE EGLK
11.
BLACKPOOL EGNH
12.
BOURNEMOUTH EGHH
13.
BRISTOL EGGD
14.
CAERNARFON EGCK
15.
CAMBRIDGE EGSC
16.
CAMPBELTOWN EGEC
17.
CARDIFF EGFF
18.
CHALGROVE EGLJ
19.
CHICHESTER/GOODWOOD EGHR
20.
COLL EGEL
21.
COLONSAY EGEY
22.
COMPTON ABBAS EGHA
23.
COVENTRY EGBE
24.
CRANFIELD EGTC
25.
CUMBERNAULD EGPG
26.
DENHAM EGLD
27.
DERBY EGBD
28.
DONCASTER SHEFFIELD EGCN
29.
DUNDEE EGPN
30.
DUNKESWELL EGTU
31.
DUXFORD EGSU
32.
EARLS COLNE EGSR
33.
EAST MIDLANDS EGNX
34.
EDAY EGED
35.
EDINBURGH EGPH
36.
ELSTREE EGTR
37.
ENNISKILLEN/ST ANGELO EGAB
38.
EXETER EGTE
39.
FAIR ISLE EGEF
40.
FAIROAKS EGTF
41.
FARNBOROUGH EGLF
42.
FENLAND EGCL
43.
GLASGOW EGPF
44.
GLOUCESTERSHIRE EGBJ
45.
GUERNSEY EGJB
46.
HAVERFORDWEST EGFE
47.
HAWARDEN EGNR
48.
HUMBERSIDE EGNJ
49.
INVERNESS EGPE
50.
ISLAY EGPI
51.
ISLE OF MAN EGNS
52.
JERSEY EGJJ
53.
KEMBLE EGBP
54.
KIRKWALL EGPA
55.
LAND'S END EGHC
56.
LASHENDEN/HEADCORN EGKH
57.
LEE-ON-SOLENT EGHF
58.
LEEDS BRADFORD EGNM
59.
LEEDS EAST EGCM
60.
LEICESTER EGBG
61.
LERWICK/TINGWALL EGET
62.
LIVERPOOL EGGP
63.
LONDON CITY EGLC
64.
LONDON GATWICK EGKK
65.
LONDON HEATHROW EGLL
66.
LONDON LUTON EGGW
67.
LONDON STANSTED EGSS
68.
LONDONDERRY/EGLINTON EGAE
69.
LYDD EGMD
70.
MANCHESTER BARTON EGCB
71.
MANCHESTER EGCC
72.
NETHERTHORPE EGNF
73.
NEWCASTLE EGNT
74.
NEWQUAY EGHQ
75.
NEWTOWNARDS EGAD
76.
NORTH RONALDSAY EGEN
77.
NORWICH EGSH
78.
NOTTINGHAM EGBN
79.
OBAN EGEO
80.
OLD BUCKENHAM EGSV
81.
OLD WARDEN EGTH
82.
OXFORD EGTK
83.
PAPA WESTRAY EGEP
84.
PERTH/SCONE EGPT
85.
PRESTWICK EGPK
86.
REDHILL EGKR
87.
RETFORD/GAMSTON EGNE
88.
ROCHESTER EGTO
89.
SANDAY EGES
90.
SANDTOFT EGCF
91.
SCILLY ISLES/ST MARY'S EGHE
92.
SHERBURN-IN-ELMET EGCJ
93.
SHOBDON EGBS
94.
SHOREHAM EGKA
95.
SLEAP EGCV
96.
SOUTHAMPTON EGHI
97.
SOUTHEND EGMC
98.
ST ATHAN EGSY
99.
STAPLEFORD EGSG
100.
STORNOWAY EGPO
101.
STRONSAY EGER
102.
SUMBURGH EGPB
103.
SWANSEA EGFH
104.
TATENHILL EGBM
105.
TEESSIDE INTERNATIONAL EGNV
106.
THRUXTON EGHO
107.
TIREE EGPU

WALNEY EGNL

WARTON EGNO

WELLESBOURNE MOUNTFORD EGBW
WELSHPOOL EGCW
WEST WALES/ABERPORTH EGFA
WESTRAY EGEW
WHITE WALTHAM EGLM
WICK EGPC
WICKENBY EGNW
WOLVERHAMPTON/HALFPENNY GREEN EGBO
WYCOMBE AIR PARK/BOOKER EGTB
YEOVIL/WESTLAND EGHG
BABICE AIRPORT EPBC

BIAŁA PODLASKA AIRFIELD EPBP

BIELSKO BIALA AIRPORT EPBA

BYDGOSZCZ IGNACY JAN PADEREWSKI AIRPORT EPBY

CEWICE AIR BASE EPCE

COPERNICUS WROCŁAW AIRPORT EPWR

DEBLIN MILITARY AIR BASE EPDE

GDAŃSK LECH WAŁĘSA AIRPORT EPGD

GÓRASZKA AIRPORT EPGO

INOWROCLAW MILITARY AIR BASE EPIR

JASTARNIA AIRPORT EPJA

JELENIA GÓRA GLIDER AIRPORT EPJG

KATOWICE INTERNATIONAL AIRPORT EPKT

KRAKÓW JOHN PAUL II INTERNATIONAL AIRPORT EPKK

KRZESINY MILITARY AIR BASE EPKS

LASK MILITARY AIR BASE EPLK

LECZYCA MILITARY AIR BASE EPLY

LOTNISKO KORNE EPKO

LUBLIN AIRPORT EPLB

MALBORK MILITARY AIR BASE EPMB

MIELEC AIRPORT EPML

MINSK MAZOWIECKI MILITARY AIR BASE EPMM

MIROSLAWIEC MILITARY AIR BASE EPMI

MODLIN AIRPORT EPMO

MUCHOWIEC AIRPORT EPKM

OKSYWIE MILITARY AIR BASE EPOK

OLSZTYN-MAZURY AIRPORT EPSY

POWIDZ MILITARY AIR BASE EPPW

POZNAŃ-ŁAWICA AIRPORT EPPO

PRUSZCZ GDANSKI AIR BASE EPPR

RADOM AIRPORT EPRA

REDZIKOWO AIR BASE EPSK

RZESZÓW-JASIONKA AIRPORT EPRZ

SUWAŁKI AIRPORT EPSU

SWIDWIN MILITARY AIR BASE EPSN

SZCZECIN-DĄBIE AIRPORT EPSD

SZCZECIN-GOLENIÓW "SOLIDARNOŚĆ" AIRPORT EPSC

TOMASZOW MAZOWIECKI MILITARY AIR BASE EPTM

WARSAW CHOPIN AIRPORT EPWA

ZIELONA GÓRA-BABIMOST AIRPORT EPZG

ŁÓDŹ WŁADYSŁAW REYMONT AIRPORT EPLL
"""

try:
    build_json_from_icao(raw_data)
except Exception as e:
    print(f"💣 Fatal error: {e}")
