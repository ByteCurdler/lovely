#!/usr/bin/python3
import sys
import argparse
import os
import sh
import time
import plistlib
import subprocess
import re

parser = argparse.ArgumentParser()
parser.add_argument("location")
parser.add_argument("-i", "--id", required=False)
parser.add_argument("-n", "--name", required=False)
parser.add_argument("-p", "--package", required=False)
args = parser.parse_args()

game_id = (args.id if args.id else
           input("ID of game (eg. MyGame): "))
game_name = (args.name if args.name else
             input("Display name of game (eg. My Wonderful Game): "))
game_package = (args.package if args.package else
                input("Package ID of game (eg. com.mycompany.mygame): "))

lib_dir = os.path.dirname(os.path.realpath(__file__)) + "/lib"

build_token = f"{game_id}_build_{time.strftime('%Y-%m-%d_%H-%M-%S')}"
build_folder = os.getcwd() + "/" + build_token
sh.mkdir(build_folder)


def fuse(exe, lovefile, fused=None):
    if fused is None:
        fused = exe
    content = open(exe, "rb").read() + open(lovefile, "rb").read()
    with open(fused, "wb") as f:
        f.write(content)


def zip(folder, zipfile):
    cwd = os.getcwd()
    sh.cd(folder)
    sh.zip("-r", "-9", zipfile, os.listdir())
    sh.cd(cwd)
    return zipfile


def build_lovefile(folder):
    return zip(folder, f"{build_folder}/{game_id}.love")


def sub_file(pattern, repl, file):
    with open(file) as f:
        text = f.read()
    text = re.sub(pattern,
                  repl,
                  text)
    with open(file, "w") as f:
        f.write(text)


def build_windows(lovefile):
    print("Making Windows executeable (untested)...")
    # To make Windows executeable:
    # - Fuse executable and .love file
    # - Zip it all
    sh.cp("-r", f"{lib_dir}/buildfiles/windows/",
          f"{build_folder}/windows_build")
    fuse(f"{build_folder}/windows_build/win32/love.exe", lovefile,
         f"{build_folder}/windows_build/win32/{game_id}.exe")
    sh.rm(f"{build_folder}/windows_build/win32/love.exe")
    zip(f"{build_folder}/windows_build/win32",
        f"{build_folder}/{game_id}-win32.zip")
    fuse(f"{build_folder}/windows_build/win64/love.exe", lovefile,
         f"{build_folder}/windows_build/win64/{game_id}.exe")
    sh.rm(f"{build_folder}/windows_build/win64/love.exe")
    zip(f"{build_folder}/windows_build/win32",
        f"{build_folder}/{game_id}-win64.zip")


def build_macos(lovefile):
    print("Making macOS Application (untested)...")
    # To make macOS Application
    # - Rename love.app to <game name>.app
    # - Copy .love to <game name>.app/Contents/Resources/
    # - Modify <game name>.app/Contents/Info.plist
    #  - Change "CFBundleIdentifier" key to something like "org.MyCompany.Game"
    #  - Change "CFBundleName" key to the display name, eg. "My Wonderful Game"
    #  - Remove "UTExportedTypeDeclarations" key and value
    # - Zip it (toplevel should _contain_ <game name>.app)
    app_dir = f"{build_folder}/macos_build/{game_id}.app"
    sh.mkdir(f"{build_folder}/macos_build/")
    sh.cp("-r", f"{lib_dir}/buildfiles/macos/love.app",
          app_dir)
    sh.cp("-r", lovefile,
          f"{app_dir}/Contents/Resources/")
    Info_plist = plistlib.load(open(f"{app_dir}/Contents/Info.plist", "rb"))

    Info_plist["CFBundleIdentifier"] = game_package
    Info_plist["CFBundleName"] = game_name
    del Info_plist["UTExportedTypeDeclarations"]

    plistlib.dump(Info_plist, open(f"{app_dir}/Contents/Info.plist", "wb"))
    zip(f"{build_folder}/macos_build",
        f"{build_folder}/{game_id}-macos.zip")


def build_linux_tar_gz(lovefile):
    print("(not) Making Linux .tar.gz")


def build_linux_appimage(lovefile):
    print("(partially) Making Linux AppImage")
    sh.cp("-r", f"{lib_dir}/buildfiles/linux/",
          f"{build_folder}/linux_build")
    sh.cd(f"{build_folder}/linux_build")
    appImages = [i for i in os.listdir(f"{build_folder}/linux_build"
                                       ) if i.endswith(".AppImage")]
    for i in appImages:
        subprocess.call([
                f"{build_folder}/linux_build/{i}",
                "--appimage-extract"], stderr=subprocess.DEVNULL)
        sh.cp(lovefile,
              f"{build_folder}/linux_build/squashfs-root/usr/lib/game.love")
        sub_file("LÖVE", game_name,
                 f"{build_folder}/linux_build/squashfs-root/love.desktop")
        sub_file(
            r'("\$@")', r"${APPIMAGE_DIR}/usr/lib/game.love \1",
            f"{build_folder}/linux_build/squashfs-root/usr/bin/wrapper-love")

        sh.rm(f"{build_folder}/linux_build/{i}")
        outfile = re.sub(r"love-[0-9\.]*",
                         f"{build_folder}/{game_id}-linux", i)
        subprocess.call([
                f"{lib_dir}/tools/appimagetool-x86_64.AppImage",
                f"{build_folder}/linux_build/squashfs-root", outfile],
                stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)


# https://love2d.org/wiki/Game_Distribution
print("Lövely v0-alpha0")


if os.path.isdir(args.location):
    print("Folder specified, making .love file...")
    lovefile = build_lovefile(args.location)
elif os.path.isfile(args.location) and args.location.endswith(".love"):
    print(".love file specified")
    lovefile = os.path.abspath(args.location)
else:
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    sys.exit(1)

build_windows(lovefile)
build_macos(lovefile)
# build_linux_tar_gz(lovefile)
build_linux_appimage(lovefile)
