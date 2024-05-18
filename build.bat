echo off
cls
pyinstaller -F eop.py --add-data "entry.pyw;." --add-data "builder.exe;."