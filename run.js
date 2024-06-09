const fs = require("fs");
const process = require("process");
const path = require("path");
const child_process = require("child_process");
var arglist = process.argv;
arglist = arglist.slice(2, arglist.length);
function getRelativeFile(target) {
    return path.join(".", target);
};
if (fs.existsSync(getRelativeFile("dist/eop.exe"))) {
    child_process.spawn(getRelativeFile("dist/eop.exe"), arglist).stdout.addListener("data", e => {
        process.stdout.write(e);
    });
} else {
    console.log("Cannot find cli.");
};