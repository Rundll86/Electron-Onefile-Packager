import subprocess, os, json


def getRelativeFile(filename):
    return os.path.join(os.path.dirname(__file__), filename)


entryProfile = json.load(open(getRelativeFile("entry_profile.json"), encoding="utf8"))
print(entryProfile)
os.chdir(getRelativeFile("app"))
subprocess.run(
    [
        getRelativeFile(entryProfile["electron"]),
        ".",
    ],
    shell=True,
)
