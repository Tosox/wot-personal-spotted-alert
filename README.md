# Personal Spotted Alert

[![Downloads (All Time)](https://img.shields.io/github/downloads/Tosox/wot-personal-spotted-alert/total.svg?label=Downloads%20(All%20Time))](https://github.com/Tosox/wot-personal-spotted-alert/releases)
[![Downloads (Latest Release)](https://img.shields.io/github/downloads/Tosox/wot-personal-spotted-alert/latest/total.svg?label=Downloads%20(Latest%20Release))](https://github.com/Tosox/wot-personal-spotted-alert/releases/latest)

## 📜 Description

The game only shows you a "Spotted" notification the very first time you spot an enemy. After that, there's no way to tell whether an enemy that pops up again was detected by you or by a teammate.

This mod solves this by showing an icon for a few seconds next to the marker of each enemy you personally detect.

## 🔧 Installation

* Download the [latest release](https://github.com/Tosox/wot-personal-spotted-alert/releases/latest)
* Drop the `.wotmod` into your game's mods folder: `<WoT folder>\mods\<version>\`
* Launch the game

## 📝 Changelog

You can check out the latest changes in [`CHANGELOG.md`](CHANGELOG.md).

## 🎥 Preview

<!-- TODO: add preview gif -->
<img src="readme-res/preview.gif" alt="Preview" width="700"/>

## 🛠️ Build from source

### Prerequisites

* [Python 2.7.18](https://www.python.org/downloads/release/python-2718/) — compiles the game bytecode
* A JDK such as [Eclipse Temurin 11](https://adoptium.net/temurin/releases/?version=11) — required by the Flex compiler
* [Apache Flex SDK 4.16.1](https://archive.apache.org/dist/flex/4.16.1/binaries/apache-flex-sdk-4.16.1-bin.zip) — compiles the marker SWF
* Adobe [`playerglobal32_0.swc`](https://fpdownload.macromedia.com/get/flashplayer/updaters/32/playerglobal32_0.swc) — not bundled with Flex, so it's a separate download

### Setup

1. Extract the Flex SDK somewhere, then drop `playerglobal32_0.swc` into it as
   `frameworks/libs/player/11.1/playerglobal.swc`.
2. Point the `FLEX_HOME` environment variable at that SDK folder.
3. Point the `PYTHON27` environment variable at your Python 2.7 executable
   (e.g. `C:\Python27\python.exe`). Skip this if you run `build.py` with Python 2.7 directly.
4. For `--install`, copy `build.local.example.json` to `build.local.json` and fill
   in your `game_dir` and `game_version`.

### Build

```bash
python build.py            # -> dist/<id>_<version>.wotmod
python build.py --install  # also copies it into the game's mods/<version> folder
```

The mod is configured through `mod.json`.

## 📄 License

Distributed under the GNU General Public License v3.0. See [`LICENSE`](LICENSE) for more information.
