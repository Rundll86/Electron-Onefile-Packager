from urllib import request, parse
import os, zipfile, argparse, subprocess, sys, shutil, json, threading, time, math


def progressbar(percent, max):
    return f"[{'='*round(percent*max)+'-'*(max-round(percent*max))}]"


def download(url: str, frontstr=""):
    def _download(count, block_size, total_size):
        percent = count * block_size / total_size
        print(
            f"Downloading: {frontstr} {progressbar(percent,10)} {round(percent*100,1)}%",
            end="\r",
        )

    filename = extract_file_name(url)
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
    ehome = os.environ.get("electron_home")


def check_ehome():
    if not ehome or not os.path.exists(ehome):
        throw("electron_home not found")


def load_config():
    global config
    try:
        config = default_config
        temp: dict = json.load(open(configname, encoding="utf8"))
        config["project"] |= temp.get("project") if temp.get("project") else {}
        config["build"] |= temp.get("build") if temp.get("build") else {}
    except:
        config = None


def run_build(cmd, typea):
    global buildok
    os.system(" ".join(cmd)) if typea else runcmd(cmd)
    buildok = True


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


class workspaceOpreator:
    def init():
        print("Initing workspace...")
        url = "https://cdn.npmmirror.com/binaries/electron/v30.0.6/electron-v30.0.6-win32-x64.zip"
        download(url, "electron")
        extract_zip_with_progress("electron-v30.0.6-win32-x64.zip", "electron")
        os.remove("electron-v30.0.6-win32-x64.zip")
        print("Registering electron_home...")
        result = runcmd(
            ["setx", "electron_home", os.path.abspath("electron/electron.exe")]
        )
        if result.returncode:
            throw("Failed to register electron_home")
        print("Creating config file...")
        json.dump(
            default_config,
            open(configname, "w", encoding="utf8"),
            ensure_ascii=False,
            indent=4,
        )
        print("Done.")

    def build():
        usetime = time.time()
        args.deep = True
        workspaceOpreator.clean()
        check_ehome()
        print("Checking write permission...")
        targetoutput = os.path.join("dist", config["project"]["name"] + ".exe")
        if os.path.exists(targetoutput):
            try:
                open(targetoutput, "wb")
            except:
                throw("Cannot write file")
        print("Setting up build temp...")
        if os.path.exists(config["build"]["temp"]):
            shutil.rmtree(config["build"]["temp"])
        os.mkdir(config["build"]["temp"])
        print("Building dist...")
        print("Copying renderer...")
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
        cmd = [
            get_relative_file("builder.exe"),
            "-F",
            get_relative_file("entry.pyw"),
            "--add-data",
            os.path.dirname(ehome) + ";electron",
            "--add-data",
            config["build"]["temp"] + ";app",
            "--name",
            config["project"]["name"],
        ]
        for i in config["build"]["nodeModules"]:
            if os.path.exists(os.path.join("node_modules", i)):
                print("Found valid module:", i)
                data_name = (
                    os.path.join("node_modules", i)
                    + ";"
                    + os.path.join("app/node_modules", i)
                )
                cmd.append("--add-data")
                cmd.append(data_name)
        threading.Thread(
            target=lambda: run_build(cmd, config["build"]["showTime"])
        ).start()
        pos = 0
        bar_length = 10
        runningbar_length = 3
        flower = "-\\|/"
        flower_pos = 0
        timer = 0
        print("Generating...Please wait.")
        while not buildok:
            # while True:
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
                f"<{data}> {flower[flower_pos]} {int((timer-timer%60)/60)}m{math.floor(timer)}s",
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
            workspaceOpreator.clean()
            sys.exit(0)
        print("Done.")

    def clean():
        print(f"Cleaning{'(Deep mode)' if args.deep else ''}...")
        base_clean()
        if args.deep:
            shutil.rmtree("dist") if os.path.exists("dist") else ""
        print("Done.")


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
    },
}
config = default_config
parser = argparse.ArgumentParser()
parser.add_argument("action")
parser.add_argument("--deep", "-d", action="store_true", default=False)
args: argtype = parser.parse_args()
ehome = None
configname = "eop.config.json"
buildok = False
init_electron_home()
load_config()
for i in workspaceOpreator.__dict__.keys():
    if check_string(args.action, i):
        workspaceOpreator.__dict__[i]()
