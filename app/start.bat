@echo off
title Skindential AI Server
echo Activating Conda Environment: yolo...
call C:\Users\III-AIPC-02\anaconda3\Scripts\activate.bat yolo
echo Starting Skindential AI Flask Server...
python server.py
pause
