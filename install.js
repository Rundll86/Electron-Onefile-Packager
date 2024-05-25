const process = require("process");
const child_process = require("child_process");
const fs = require('fs');
const path = require('path');
console.log("Initing...");
function countstr(str, count) {
    let res = "";
    for (let i = 0; i < count; i++) { res += str; };
    return res;
};
function relativeFile(pathes) {
    return path.join(__dirname, pathes);
};
child_process.exec("python --version").addListener("exit", e => {
    if (e !== 0) {
        console.log("Python isnt installed.");
        process.exit(1);
    };
    child_process.exec("pip --version").addListener("exit", e => {
        if (e !== 0) {
            console.log("PIP isnt installed.");
            process.exit(1);
        };
        console.log(("Building core..."));
        let installProgress = child_process.exec("pip install pyinstaller");
        let ok = false;
        installProgress.addListener("exit", () => {
            ok = true;
        });
        let flower = "-\\|/",
            flower_pos = 0;
        let pos = 0, bar_length = 10, runningbar_length = 3;
        function _run(cb = () => { }) {
            if (ok) {
                console.log(countstr(" ", 30));;
                cb();
                return;
            };
            let data = "";
            for (let i = 0; i < bar_length; i++) {
                if ((i >= pos && i <= pos + runningbar_length - 1) || (i > pos - (bar_length + 1) && i < pos - (bar_length - runningbar_length))) {
                    data += "=";
                } else {
                    data += "-";
                };
            };
            pos++;
            if (pos == bar_length + 1) {
                pos = 1;
            };
            process.stdout.write(`<${data}> ${flower[flower_pos]} Please wait...\r`);
            flower_pos++;
            if (flower_pos === flower.length) {
                flower_pos = 0;
            };
            setTimeout(() => _run(cb), 200);
        };
        _run(() => {
            try { fs.rmSync("pyinstaller.exe") } catch { };
            let cmd = `copy "${child_process.execSync("where pyinstaller").toString().split("\n")[0]}" "${__dirname}"`;
            child_process.execSync(cmd);
            console.log("Built successfully.");
            console.log("Building CLI...");
            let A = child_process.spawn("pyinstaller", [
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
            A.addListener("exit", e => {
                ok = true;
            });
            ok = false;
            _run();
        });
    });
});