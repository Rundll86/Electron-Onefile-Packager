const process = require("process");
const child_process = require("child_process");
const fs = require('fs');
child_process.exec("python --version").addListener("exit", e => {
    if (e !== 0) {
        throw new Error("Cannot find python.");
    };
    child_process.exec("python version_test.py").addListener("exit", e => {
        if (e !== 0) {
            throw new Error("Require python >= 3.9.7.");
        };
        child_process.exec("pip --version").addListener("exit", e => {
            if (e !== 0) {
                throw new Error("Cannot find pip.");
            };
            let installProgress = child_process.exec("pip install pyinstaller");
            installProgress.addListener("exit", e => {
                if (e === 0) {
                    try { fs.rmSync("pyinstaller.exe") } catch { };
                    child_process.execSync(`copy "${child_process.execSync("where pyinstaller").toString().split("\n")[0]}" "${__dirname}"`);
                    child_process.spawn("pyinstaller", [
                        "-F",
                        "eop.py",
                        "--add-data",
                        "entry.pyw;.",
                        "--add-data",
                        "pyinstaller.exe;.",
                        "--add-data",
                        "favicon.ico;.",
                        "--add-data",
                        "build.spec;.",
                        "--add-data",
                        "package.json;.",
                        "--add-data",
                        "presets;presets"
                    ]).addListener("exit", e => {
                        throw new Error("Failed to build cli.");
                    });
                } else {
                    throw new Error("Failed to build cli.");
                };
            });
        });
    });
});