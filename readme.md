**The CLI tools can generate a electron project's executable file(Only one file!)**  
Usage:
- Init: `build.bat`.
- Set `dist/eop.exe` to evironment.
- Init project profile: `eop init`
- Build executable file: `eop build`
- Clean workspace: `eop clean`

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
        "includesNodeModules": false
    }
}
```
