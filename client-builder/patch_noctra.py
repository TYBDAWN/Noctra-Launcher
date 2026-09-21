#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, struct, sys, zlib
from pathlib import Path

UPSTREAM_COMMIT = "82549ea546affe905ef735852b2f163684ddad74"

def replace_in_file(path: Path, replacements):
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")

def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

def write_noctra_logo(path: Path, size: int = 500):
    cx = cy = size // 2
    pixels = bytearray()
    for y in range(size):
        row = bytearray()
        t = y / max(1, size - 1)
        pr = int(139 * (1 - t) + 79 * t)
        pg = int(92 * (1 - t) + 70 * t)
        pb = int(246 * (1 - t) + 229 * t)
        for x in range(size):
            manhattan = abs(x - cx) + abs(y - cy)
            diamond = 184 <= manhattan <= 214
            left_bar = 146 <= x <= 184 and 136 <= y <= 364
            right_bar = 316 <= x <= 354 and 136 <= y <= 364
            expected_x = 173 + int((y - 136) * (162 / 228)) if 136 <= y <= 364 else -999
            diagonal = 136 <= y <= 364 and abs(x - expected_x) <= 19
            if diamond:
                rgba = (pr, pg, pb, 255)
            elif left_bar or right_bar or diagonal:
                rgba = (245, 243, 255, 255)
            else:
                rgba = (0, 0, 0, 0)
            row.extend(rgba)
        pixels.extend(b"\x00" + row)
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", header) + png_chunk(b"IDAT", zlib.compress(bytes(pixels), 9)) + png_chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch_noctra.py <velo-source-dir>")
    root = Path(sys.argv[1]).resolve()
    if not (root / "src").exists():
        raise SystemExit(f"Not a Velo source checkout: {root}")

    source_roots = [root / "src", root / "build.gradle.kts", root / "settings.gradle.kts", root / "stonecutter.properties.toml"]
    files = []
    for entry in source_roots:
        if entry.is_file():
            files.append(entry)
        elif entry.exists():
            files.extend(p for p in entry.rglob("*") if p.is_file() and p.suffix.lower() in {".java",".json",".properties",".kts",".toml"})

    replacements = [
        ("VELO CLIENT", "NOCTRA"),
        ("Velo Client", "Noctra Client"),
        ("Velo Network", "Noctra Network"),
        ("Velo Dark", "Noctra Eclipse"),
        ("Velo Coins", "Noctra Credits"),
        ("Velo:", "Noctra:"),
        ("velo-client", "noctra-client"),
    ]
    for path in files:
        replace_in_file(path, replacements)

    replace_in_file(root / "src/main/java/net/veloclient/velo/config/VeloPaths.java", [("VeloClient", "NoctraClient")])
    replace_in_file(root / "stonecutter.properties.toml", [('mod.version = "0.7.0"', 'mod.version = "2.0.0"')])

    mod_json = root / "src/main/resources/fabric.mod.json"
    data = json.loads(mod_json.read_text(encoding="utf-8"))
    data["id"] = "noctra-client"
    data["name"] = "Noctra Client"
    data["description"] = "A polished Minecraft Java QoL, HUD, performance and cosmetics client built on the MIT-licensed Velo Client foundation."
    data["authors"] = ["Noctra Project", "Velo Client Contributors (upstream MIT)"]
    data["contact"] = {
        "homepage": "https://github.com/TYBDAWN/Noctra-Launcher",
        "sources": "https://github.com/TYBDAWN/Noctra-Launcher",
        "issues": "https://github.com/TYBDAWN/Noctra-Launcher/issues",
    }
    mod_json.write_text(json.dumps(data, indent="\t") + "\n", encoding="utf-8")

    old_assets = root / "src/client/resources/assets/velo-client"
    new_assets = root / "src/client/resources/assets/noctra-client"
    if old_assets.exists() and not new_assets.exists():
        new_assets.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_assets), str(new_assets))

    for old_name, new_name in [
        ("velo-client.client.mixins.json", "noctra-client.client.mixins.json"),
        ("velo-client.client.optional.mixins.json", "noctra-client.client.optional.mixins.json"),
    ]:
        old = root / "src/client/resources" / old_name
        new = root / "src/client/resources" / new_name
        if old.exists() and not new.exists():
            old.rename(new)

    write_noctra_logo(new_assets / "textures/icon/logo.png")

    title = root / "src/client/java/net/veloclient/velo/client/gui/title/TitleScreenTheme.java"
    replace_in_file(title, [("0xFFF24759", "0xFF8B5CF6")])

    presets = root / "src/client/java/net/veloclient/velo/client/theme/ThemePresets.java"
    replace_in_file(presets, [
        ('"Noctra Eclipse", 0xF00F0A0A, 0xE01E1212, 0xFFFF4444, 0xFFB71C1C, 0xFFFFFFFF, 8, 0.6f, 1.0f, 0.85f',
         '"Noctra Eclipse", 0xF0080912, 0xE0121020, 0xFF8B5CF6, 0xFF4F46E5, 0xFFF4F1FF, 8, 0.62f, 1.05f, 0.88f')
    ])

    network_cfg = root / "src/client/java/net/veloclient/velo/client/network/VeloNetworkConfig.java"
    replace_in_file(network_cfg, [
        ('public static final String DEFAULT_SERVER_URL = "https://client.asteriasmp.net";',
         'public static final String DEFAULT_SERVER_URL = "";')
    ])
    network_module = root / "src/client/java/net/veloclient/velo/client/modules/utility/VeloNetworkModule.java"
    replace_in_file(network_module, [
        ('ModuleCategory.COSMETICS, SafetyTag.COSMETIC_ONLY, true);',
         'ModuleCategory.COSMETICS, SafetyTag.COSMETIC_ONLY, false);')
    ])

    (root / "NOCTRA-UPSTREAM-NOTICE.md").write_text(
        "# Noctra upstream notice\n\n"
        "Noctra Client v2 is a derivative of Velo Client at commit " + UPSTREAM_COMMIT + ".\n\n"
        "Velo Client is Copyright (c) 2026 Velo Client Contributors and is licensed under the MIT License. "
        "The original LICENSE file is preserved unchanged and included by the upstream Gradle build.\n",
        encoding="utf-8"
    )
    print("Noctra patch complete")

if __name__ == "__main__":
    main()
