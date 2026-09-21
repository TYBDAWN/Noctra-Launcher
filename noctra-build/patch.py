#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, struct, sys, zlib
from pathlib import Path

UPSTREAM_COMMIT="82549ea546affe905ef735852b2f163684ddad74"

def replace(path, pairs):
    txt=path.read_text(encoding="utf-8")
    old=txt
    for a,b in pairs: txt=txt.replace(a,b)
    if txt!=old: path.write_text(txt,encoding="utf-8")

def chunk(t,d):
    return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)

def logo(path,size=500):
    cx=cy=size//2
    raw=bytearray()
    for y in range(size):
        row=bytearray()
        t=y/(size-1)
        pr=int(139*(1-t)+79*t); pg=int(92*(1-t)+70*t); pb=int(246*(1-t)+229*t)
        for x in range(size):
            d=abs(x-cx)+abs(y-cy)
            diamond=184<=d<=214
            l=146<=x<=184 and 136<=y<=364
            r=316<=x<=354 and 136<=y<=364
            ex=173+int((y-136)*(162/228)) if 136<=y<=364 else -999
            diag=136<=y<=364 and abs(x-ex)<=19
            if diamond: rgba=(pr,pg,pb,255)
            elif l or r or diag: rgba=(245,243,255,255)
            else: rgba=(0,0,0,0)
            row.extend(rgba)
        raw.extend(b"\x00"+row)
    hdr=struct.pack(">IIBBBBB",size,size,8,6,0,0,0)
    png=b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",hdr)+chunk(b"IDAT",zlib.compress(bytes(raw),9))+chunk(b"IEND",b"")
    path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(png)

root=Path(sys.argv[1]).resolve()
files=[]
for entry in [root/"src",root/"build.gradle.kts",root/"settings.gradle.kts",root/"stonecutter.properties.toml"]:
    if entry.is_file(): files.append(entry)
    elif entry.exists(): files += [p for p in entry.rglob("*") if p.is_file() and p.suffix.lower() in {".java",".json",".properties",".kts",".toml"}]

pairs=[
 ("VELO CLIENT","NOCTRA"),
 ("Velo Client","Noctra Client"),
 ("Velo Network","Noctra Network"),
 ("Velo Dark","Noctra Eclipse"),
 ("Velo Coins","Noctra Credits"),
 ("Velo:","Noctra:"),
 ("velo-client","noctra-client"),
]
for p in files: replace(p,pairs)

replace(root/"src/main/java/net/veloclient/velo/config/VeloPaths.java",[("VeloClient","NoctraClient")])
replace(root/"stonecutter.properties.toml",[
 ('mod.version = "0.7.0"','mod.version = "2.0.0"')
])

mod=root/"src/main/resources/fabric.mod.json"
d=json.loads(mod.read_text(encoding="utf-8"))
d["id"]="noctra-client"
d["name"]="Noctra Client"
d["description"]="Noctra Client: a polished Minecraft Java QoL, HUD, performance and cosmetics client built on the MIT-licensed Velo Client foundation."
d["authors"]=["Noctra Project","Velo Client Contributors (upstream MIT)"]
d["contact"]={"homepage":"https://github.com/TYBDAWN/Noctra-Launcher","sources":"https://github.com/TYBDAWN/Noctra-Launcher","issues":"https://github.com/TYBDAWN/Noctra-Launcher/issues"}
mod.write_text(json.dumps(d,indent="\t")+"\n",encoding="utf-8")

oldassets=root/"src/client/resources/assets/velo-client"; newassets=root/"src/client/resources/assets/noctra-client"
if oldassets.exists():
    if newassets.exists(): shutil.rmtree(newassets)
    newassets.parent.mkdir(parents=True,exist_ok=True); shutil.move(str(oldassets),str(newassets))
for a,b in [("velo-client.client.mixins.json","noctra-client.client.mixins.json"),("velo-client.client.optional.mixins.json","noctra-client.client.optional.mixins.json")]:
    old=root/"src/client/resources"/a; new=root/"src/client/resources"/b
    if old.exists():
        if new.exists(): new.unlink()
        old.rename(new)

logo(newassets/"textures/icon/logo.png")
replace(root/"src/client/java/net/veloclient/velo/client/gui/title/TitleScreenTheme.java",[("0xFFF24759","0xFF8B5CF6")])
replace(root/"src/client/java/net/veloclient/velo/client/theme/ThemePresets.java",[
 ('"Noctra Eclipse", 0xF00F0A0A, 0xE01E1212, 0xFFFF4444, 0xFFB71C1C, 0xFFFFFFFF, 8, 0.6f, 1.0f, 0.85f',
  '"Noctra Eclipse", 0xF0080912, 0xE0121020, 0xFF8B5CF6, 0xFF4F46E5, 0xFFF4F1FF, 8, 0.62f, 1.05f, 0.88f')
])
replace(root/"src/client/java/net/veloclient/velo/client/network/VeloNetworkConfig.java",[
 ('public static final String DEFAULT_SERVER_URL = "https://client.asteriasmp.net";','public static final String DEFAULT_SERVER_URL = "";')
])
replace(root/"src/client/java/net/veloclient/velo/client/modules/utility/VeloNetworkModule.java",[
 ('ModuleCategory.COSMETICS, SafetyTag.COSMETIC_ONLY, true);','ModuleCategory.COSMETICS, SafetyTag.COSMETIC_ONLY, false);')
])
(root/"NOCTRA-UPSTREAM-NOTICE.md").write_text(
 "# Noctra upstream notice\n\nNoctra Client v2 is derived from Velo Client at commit "+UPSTREAM_COMMIT+
 ".\n\nVelo Client is Copyright (c) 2026 Velo Client Contributors and licensed under MIT. The original LICENSE is preserved.\n",
 encoding="utf-8")
print("Noctra patch complete")
