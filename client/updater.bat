@echo off
title updateing
curl -L -O https://github.com/anhlocvu/play-vnt/releases/latest/download/play_vnt_client.zip
powershell Expand-Archive -Path "play_vnt_client.zip" -DestinationPath "."
del play_vnt_client.zip
y
start play_vnt.exe