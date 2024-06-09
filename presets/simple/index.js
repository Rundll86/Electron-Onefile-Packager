const { app, BrowserWindow, Menu } = require("type-electron");
app.addListener("ready", () => {
    const win = new BrowserWindow({
        width: 1280,
        height: 720
    });
    win.loadFile("index.html");
    Menu.setApplicationMenu(null);
});
app.addListener("window-all-closed", () => app.quit());