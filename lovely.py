#!/usr/bin/python3
import sys
import argparse
import os
import sh
import time

parser = argparse.ArgumentParser()
parser.add_argument("location")
parser.add_argument("-n", "--name", required=False)
args = parser.parse_args()

game_id = args.name if args.name else input("ID name of game: ")

lib_dir = os.path.dirname(os.path.realpath(__file__)) + "/lib"

build_token = f"{game_id}_build_{time.strftime('%Y-%m-%d_%H-%M-%S')}"
build_folder = os.getcwd() + "/" + build_token
sh.mkdir(build_folder)


def fuse(exe, lovefile, fused=None):
    if fused is None:
        fused = exe
    with open(fused, "wb") as f:
        f.write(open(exe, "rb").read() + open(lovefile, "rb").read())


def zip(folder, zipfile):
    cwd = os.getcwd()
    sh.cd(folder)
    sh.zip("-r", zipfile, os.listdir())
    sh.cd(cwd)
    return zipfile


def build_lovefile(folder):
    return zip(folder, f"{build_folder}/{game_id}.love")


def build_windows(lovefile):
    print("Making Windows executeable (untested)...")
    # To make Windows executeable:
    # - Fuse executable and .love file
    # - Zip it all
    sh.cp("-r", f"{lib_dir}/buildfiles/windows/", f"{build_folder}/windows_build")
    fuse(f"{build_folder}/windows_build/win32/love.exe", lovefile)
    zip(f"{build_folder}/windows_build/win32",
        f"{build_folder}/{game_id}-win32.zip")
    fuse(f"{build_folder}/windows_build/win64/love.exe", lovefile)
    zip(f"{build_folder}/windows_build/win32",
        f"{build_folder}/{game_id}-win64.zip")


def build_macos(lovefile):
    print("(not) Making macOS Application...")
    # TODO make macOS Application
    # - Rename love.app to <game name>.app
    # - Copy .love to <game name>.app/Contents/Resources/
    # - Modify <game name>.app/Contents/Info.plist
    #  - Change "CFBundleIdentifier" key to something like "org.MyCompany.Game"
    #  - Change "CFBundleName" key to the display name, eg. "My Wonderful Game"
    #  - Remove "UTExportedTypeDeclarations" key and value
    # - Zip it (toplevel should _contain_ <game name>.app)


def build_linux_tar_gz(lovefile):
    print("(not) Making Linux .tar.gz")


def build_linux_appimage(lovefile):
    print("(not) Making Linux AppImage")


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
build_linux_tar_gz(lovefile)
build_linux_appimage(lovefile)
