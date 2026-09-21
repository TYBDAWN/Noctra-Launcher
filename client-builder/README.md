# Noctra Client v2 — Velo Foundation

This builder creates **Noctra Client v2 for Fabric 1.21.11 / Java 21** from the MIT-licensed Velo Client foundation.

Instead of copying a random compiled JAR, the build pins an exact upstream commit, applies auditable Noctra patches, and compiles with the project's real Gradle/Fabric Loom setup.

## Foundation features

- Real Right Shift module UI with mouse cursor
- Draggable HUD editor with scaling/grid snapping
- Profiles and per-server profiles
- Genuine FreeLook/Perspective camera implementation
- Zoom, toggle sprint/sneak, keystrokes, CPS, FPS, ping, coordinates
- Armor/durability, potions, held item, session stats, waypoints and minimap
- Performance controls, frame-time graph, memory/GPU monitors
- Rendering tools, server/debug overlays, log viewer
- Custom crosshair, keybind system, themes and cosmetics/capes

## Noctra changes

- Noctra Client identity and Fabric mod id
- Original generated Noctra logo instead of Velo's logo art
- Dark violet **Noctra Eclipse** default theme
- `%APPDATA%/NoctraClient` / `~/.noctra-client` config root
- Noctra project metadata/contact links
- Velo's hosted cross-player network is disabled by default
- Upstream MIT license/copyright notice remains preserved

## Upstream

Velo Client: https://github.com/velo345/velo-client

Pinned upstream commit: `82549ea546affe905ef735852b2f163684ddad74`

Velo Client is MIT licensed. The original LICENSE is preserved unchanged by the build.
