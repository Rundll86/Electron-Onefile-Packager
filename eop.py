from urllib import request, parse
import os, zipfile, argparse, subprocess, sys, shutil, json, threading, time, math


def progressbar(percent, max):
    return f"[{'='*round(percent*max)+'-'*(max-round(percent*max))}]"


def download(url: str, frontstr=""):
    global lastsize

    def _download(count, block_size, total_size):
        global lastsize
        percent = count * block_size / total_size
        newsize = os.path.getsize(filename)
        print(
            f"Downloading: {frontstr} {progressbar(percent,10)} {round(percent*100,1)}% {newsize-lastsize}Kb/s",
            end="\r",
        )
        lastsize = newsize

    filename = extract_file_name(url)
    lastsize = 0
    request.urlretrieve(url, filename, reporthook=_download)
    print("")


def get_relative_file(filename):
    return os.path.join(os.path.dirname(__file__), filename)


def extract_file_name(url: str):
    return os.path.basename(parse.urlsplit(url).path)


def extract_zip_with_progress(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        inflist = zip_ref.infolist()
        extracted = 0
        for file in inflist:
            zip_ref.extract(file, extract_to)
            extracted += 1
            print(
                f"Extracting: {extract_to} {progressbar(extracted/len(inflist),10)} {round(extracted/len(inflist)*100,1)}%",
                end="\r",
            )
    print("")


def throw(msg):
    print(f"Failed: {msg}.")
    sys.exit(1)


def check_string(a: str, b: str):
    return a.upper() == b.upper()


def runcmd(cmd):
    return subprocess.run(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def init_electron_home():
    global ehome
    ehome = os.path.join(config["electron"]["home"], config["electron"]["bin"])


def check_ehome():
    if not ehome or not os.path.exists(ehome):
        throw("electron home is invalid")


def load_config():
    global config
    config = default_config
    try:
        temp: dict = json.load(open(configname, encoding="utf8"))
        for i in default_config.keys():
            config[i] |= temp.get(i) if temp.get(i) else {}
    except Exception as e:
        print("Failed to load profile, using default.", e)
        config = default_config


def run_build(cmd, typea):
    global buildok
    rtcode = os.system(" ".join(cmd)) if typea else runcmd(cmd).returncode
    buildok = True
    return not rtcode


def base_clean():
    (
        shutil.rmtree(config["build"]["temp"])
        if os.path.exists(config["build"]["temp"])
        else ""
    )
    shutil.rmtree("build") if os.path.exists("build") else ""
    (
        os.remove(config["project"]["name"] + ".spec")
        if os.path.exists(config["project"]["name"] + ".spec")
        else ""
    )


class argtype:
    action: str
    deep: bool
    skip: list[str]
    use_preset: list[str]


class workspaceOpreator:
    def version():
        print("Version:", npm_package["version"])
        print("Github: Rundll86/Electron-Onefile-Packager")
        print("NPM: electron-ofp")
        print("Bilibili: 649063815")

    def init():
        print("Initing workspace...")
        things = 0
        if "electron" not in args.skip:
            url = "https://cdn.npmmirror.com/binaries/electron/v30.0.6/electron-v30.0.6-win32-x64.zip"
            download(url, "electron")
            extract_zip_with_progress("electron-v30.0.6-win32-x64.zip", "electron")
            os.remove("electron-v30.0.6-win32-x64.zip")
            config["electron"]["home"] = "electron"
            things += 1
        if "profile" not in args.skip:
            print("Creating config file...")
            json.dump(
                default_config,
                open(configname, "w", encoding="utf8"),
                ensure_ascii=False,
                indent=4,
            )
            things += 1
        if len(args.use_preset) == 0:
            print(
                "You can use a project preset to init.",
                "By giving --use-preset <name>.",
            )
            print("Avaliable:", ", ".join(os.listdir(get_relative_file("presets"))))
        else:
            for i in args.use_preset:
                preset_path = get_relative_file(os.path.join("presets", i))
                if os.path.exists(preset_path) and os.path.isdir(preset_path):
                    shutil.copytree(preset_path, ".", dirs_exist_ok=True)
                    print(f"Using perset [{i}].")
                    things += 1
                else:
                    print(f"Cannot find any presets named {i}, Skipped.")
        print("Done." if things > 0 else "Nothing to do.")

    def build():
        usetime = time.time()
        args.deep = True
        check_ehome()
        print("Checking write permission...")
        targetoutput = os.path.join("dist", config["project"]["name"] + ".exe")
        if os.path.exists(targetoutput):
            try:
                open(targetoutput, "wb")
            except:
                throw("Cannot write file")
        workspaceOpreator.clean()
        if os.path.exists(config["build"]["temp"]):
            shutil.rmtree(config["build"]["temp"])
        os.mkdir(config["build"]["temp"])
        print("Loading resource...")
        shutil.copy(config["project"]["entry"], config["build"]["temp"])
        for i in config["project"]["files"]:
            shutil.copy(i, config["build"]["temp"])
        for i in config["project"]["dirs"]:
            shutil.copytree(i, os.path.join(config["build"]["temp"], i))
        for i in config["project"]["excludes"]:
            target = os.path.join(config["build"]["temp"], i)
            if os.path.exists(i) and os.path.exists(target):
                if os.path.isdir(i):
                    shutil.rmtree(target)
                if os.path.isfile(i):
                    os.remove(target)
        json.dump(
            {"main": config["project"]["entry"]},
            open(
                os.path.join(config["build"]["temp"], "package.json"),
                "w",
                encoding="utf8",
            ),
            ensure_ascii=False,
        )
        iconpath = (
            config["build"]["icon"]
            if os.path.exists(config["build"]["icon"])
            else get_relative_file("favicon.ico")
        )
        print("Loading node_modules...")
        _nmsl = []
        for i in config["build"]["nodeModules"]:
            abspath = os.path.abspath(os.path.join("node_modules", i))
            if os.path.exists(abspath):
                print("Found a valid node_module:", i)
                _nmsl.append((abspath, "app/node_modules/" + i))
        print("Generating entry profile...")
        json.dump(
            {
                "electron": os.path.join("electron", config["electron"]["bin"]),
                "version": npm_package["version"],
                "app": config["project"]["name"],
                "show": config["build"]["showEntryInfo"],
            },
            open(get_relative_file("entry_profile.json"), "w", encoding="utf8"),
            ensure_ascii=False,
        )
        print("Generating build spec...")
        datas = [
            (os.path.abspath(os.path.dirname(ehome)).replace("\\", "/"), "electron"),
            (os.path.abspath(config["build"]["temp"]).replace("\\", "/"), "app"),
            (get_relative_file("entry_profile.json"), "."),
        ]
        datas.extend(_nmsl)
        buildspec = (
            open(get_relative_file("build.spec"), encoding="utf8")
            .read()
            .replace("_name_", config["project"]["name"])
            .replace("_main_", get_relative_file("entry.pyw").replace("\\", "/"))
            .replace("_datas_", repr(datas))
            .replace("_icon_", iconpath.replace("\\", "/"))
            .replace("_console_", repr(config["build"]["showConsole"]))
        )
        specname = f"{config['project']['name']}.spec"
        open(specname, "w", encoding="utf8").write(buildspec)
        threading.Thread(
            target=lambda: run_build(
                [get_relative_file("pyinstaller.exe"), specname],
                config["build"]["showTime"],
            )
        ).start()
        pos = 0
        bar_length = 10
        runningbar_length = 3
        flower = "-\\|/"
        flower_pos = 0
        timer = 0
        print("Generating executable file...Please wait.")
        while not buildok:
            data = ""
            for i in range(bar_length):
                if (i >= pos and i <= pos + runningbar_length - 1) or (
                    i > pos - (bar_length + 1)
                    and i < pos - (bar_length - runningbar_length)
                ):
                    data += "="
                else:
                    data += "-"
            pos += 1
            if pos == bar_length + 1:
                pos = 1
            print(
                f"<{data}> {flower[flower_pos]} {math.floor(timer)}s",
                end="\r",
                flush=True,
            )
            flower_pos += 1
            if flower_pos == len(flower):
                flower_pos = 0
            time.sleep(0.2)
            timer += 0.2
        usetime = int(time.time() - usetime)
        print(f"Generated successfully. Use: {usetime}s" + " " * (runningbar_length))
        if config["build"]["clean"]:
            args.deep = False
            workspaceOpreator.clean()
            sys.exit(0)
        print("Done.")

    def clean():
        print(f"Cleaning{'(Deep mode)' if args.deep else ''}...")
        base_clean()
        if args.deep:
            shutil.rmtree("dist") if os.path.exists("dist") else ""
        print("Done.")

    def start():
        check_ehome()
        subprocess.run([ehome, config["project"]["entry"]])


parser = argparse.ArgumentParser()
parser.add_argument("action")
parser.add_argument("--deep", "-d", action="store_true", default=False)
parser.add_argument("--skip", "-s", nargs="+", default=[])
parser.add_argument("--use-preset", "-p", nargs="+", default=[])
args: argtype = parser.parse_args()
unset_type = "!!UNSET"
default_config = {
    "project": {
        "name": "some-app",
        "entry": "index.js",
        "files": [],
        "dirs": [],
        "excludes": [],
    },
    "build": {
        "temp": "temp",
        "clean": False,
        "nodeModules": [],
        "showTime": False,
        "showConsole": False,
        "showEntryInfo": True,
        "icon": "favicon.ico",
    },
    "electron": {
        "home": unset_type if "electron" in args.skip else "./electron",
        "bin": "electron.exe",
    },
}
config = default_config
configname = "eop.config.json"
buildok = False
npm_package = json.load(open(get_relative_file("package.json"), encoding="utf8"))
load_config()
init_electron_home()
print(f"Electron-OFP v{npm_package['version']}.")
print("Command:", args.action.upper(), "\n")
command_ok = False
for i in workspaceOpreator.__dict__.keys():
    if check_string(args.action, i):
        command_ok = True
        workspaceOpreator.__dict__[i]()
if not command_ok:
    print("Invalid command!")
