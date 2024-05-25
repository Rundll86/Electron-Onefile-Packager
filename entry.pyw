import subprocess, os, json


def getRelativeFile(filename):
    return os.path.join(os.path.dirname(__file__), filename)


os.chdir(getRelativeFile("app"))
subprocess.run(
    [
        json.load(open(getRelativeFile("entry_profile.json"), encoding="utf8"))["electron"],
        ".",
    ],
    shell=True
)
