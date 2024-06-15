echo off
cls
push.bat && npm version patch && npm publish && push.bat && npm version patch && npm publish && npm update electron-ofp -g