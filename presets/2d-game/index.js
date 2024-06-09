const { app, BrowserWindow, Menu } = require("type-electron");
const path = require("path");
const fs = require("fs");
const config = JSON.parse(fs.readFileSync(path.join(__dirname, "config.json"), "utf-8").toString());
app.addListener("ready", () => {
    const win = new BrowserWindow({
        width: 1280,
        height: 720,
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
            nodeIntegration: true
        }
    });
    win.loadFile("1.html");
    config.devtool ? win.webContents.openDevTools() : null;
    Menu.setApplicationMenu(null);
});
app.addListener("window-all-closed", () => app.quit());