from urllib import request, parse
import os, zipfile, argparse, subprocess, sys, shutil, json, threading, time


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
args = parser.parse_args()
ehome = None
configname = "eop.config.json"
buildok = False
init_electron_home()
load_config()


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
            default_config, open(configname, "w", encoding="utf8"), ensure_ascii=False
        )
        print("Done.")

    def build():
        workspaceOpreator.clean()
        check_ehome()
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
                cmd.append("--add-data")
                cmd.append(
                    os.path.join("node_modules", i)
                    + ";"
                    + os.path.join("app/node_modules", i)
                )
        print(" ".join(cmd))
        threading.Thread(
            target=lambda: run_build(cmd, config["build"]["showTime"])
        ).start()
        pos = 0
        offs = 1
        print("Generating...Please wait.")
        while not buildok:
            data = ""
            for i in range(10):
                if pos >= i and pos <= i + 3:
                    data += "="
                else:
                    data += "-"
            pos += offs
            if pos == 12:
                offs = -1
            elif pos == 0:
                offs = 1
            print(f"<{data}>", end="\r", flush=True)
            time.sleep(0.2)
        print("Generated successfully." + " " * 10)
        if config["build"]["clean"]:
            workspaceOpreator.clean()
            sys.exit(0)
        print("Done.")

    def clean():
        print("Cleaning...")
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
        print("Done.")


for i in workspaceOpreator.__dict__.keys():
    if check_string(args.action, i):
        workspaceOpreator.__dict__[i]()
