import subprocess, os


def getRelativeFile(filename):
    return os.path.join(os.path.dirname(__file__), filename)


os.chdir(getRelativeFile("app"))
subprocess.run([getRelativeFile("electron/electron.exe"), "."])
