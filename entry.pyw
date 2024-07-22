import subprocess, os, json


def getRelativeFile(filename):
    return os.path.join(os.path.dirname(__file__), filename)


entryProfile = json.load(open(getRelativeFile("entry_profile.json"), encoding="utf8"))
if entryProfile["show"]:
    print(f"Electron-OFP v{entryProfile['version']}.")
    print(f"ApplicationName: {entryProfile['app']}.")
    print(f"ElectronCore: {entryProfile['electron']}.")
os.chdir(getRelativeFile("app"))
print([
        getRelativeFile(entryProfile["electron"]),
        ".",
    ])
process = subprocess.Popen(
    [
        getRelativeFile(entryProfile["electron"]),
        ".",
    ],
    shell=True,
    stdout=subprocess.STDOUT,
    stderr=subprocess.STDOUT,
    stdin=subprocess.STDOUT,
)
process.wait()
