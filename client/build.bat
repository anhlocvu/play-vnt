@echo off

python -m nuitka --standalone --windows-console=disable --remove-output -o "play_vnt.exe" client.py
xcopy "sounds" "client.dist\sounds" /E /I /Y
echo "Successfully built the client."
pause