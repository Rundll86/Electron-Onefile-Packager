const process = require("process");
const child_process = require("child_process");
const fs = require('fs');
child_process.exec("python --version").addListener("exit", e => {
    if (e !== 0) {
        process.exit(1);
    };
    child_process.exec("pip --version").addListener("exit", e => {
        if (e !== 0) {
            process.exit(1);
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
                    "build.spec;."
                ]);
            } else {
                process.exit(1);
            };
        });
    });
});