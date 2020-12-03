# LÖVEly
A packager for LÖVE to AppImage, Windows, macOS

# Usage
```
python3 lovely.py <project> [-i/--id <id>] [-n/--name <name>] [-p/--package <package>]
```

where:
- <project> is a .love file or a folder
- <id> is a string used as filenames, eg. "MyGreatGame"
- <name> is the display name of the game, eg. "My Great Game"
- <package> is a macOS/Android package name, eg. "com.example.mygreatgame"

## Untested builds:
- All macOS builds
- Windows 32-bit (64-bit tested with WineHQ)
- Linux i686 build
