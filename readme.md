**The CLI tools can generate a electron project's executable file(Only one file!)**  
Usage:
- Init: `node install.js`
- Set `dist/eop.exe` to environment
- Init project profile: `eop init [--skip-electron]`
- Build executable file: `eop build`
- Clean workspace: `eop clean [--deep]`

A project profile usually be:
```json
{
    "project": {
        "name": "some-app",
        "entry": "index.js",
        "files": [
        ],
        "dirs": [
        ],
        "excludes": [
        ]
    },
    "build": {
        "temp": "temp",
        "clean": false,
        "nodeModules": [],
        "showTime": false,
        "showEntryInfo": true,
        "includesNodeModules": false
    },
    "electron": {
        "home": "electron",
        "bin": "electron.exe"
    }
}
```
