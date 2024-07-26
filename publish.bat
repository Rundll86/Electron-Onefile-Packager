echo off
cls
npm config set registry=https://registry.npmjs.org && push.bat && npm version patch && npm publish && npm update electron-ofp -g