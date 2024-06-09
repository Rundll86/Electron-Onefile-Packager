const { contextBridge } = require("type-electron");
const path = require("path");
const fs = require("fs");
contextBridge.exposeInMainWorld("config", JSON.parse(fs.readFileSync(path.join(__dirname, "config.json"), "utf-8").toString()));