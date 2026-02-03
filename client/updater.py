"""Client updater for play vnt."""

import os
import sys
import subprocess
import requests
import wx
from constants import VERSION, GAME_NAME

UPDATE_URL = "https://raw.githubusercontent.com/anhlocvu/play-vnt/main/version.txt"

def check_for_updates():
    """Check for updates on GitHub and prompt user if available."""
    try:
        response = requests.get(UPDATE_URL, timeout=5)
        response.raise_for_status()
        latest_version = response.text.strip()
        
        if latest_version != VERSION:
            # Create a temporary app if one doesn't exist to show dialog
            app = wx.GetApp()
            if not app:
                app = wx.App(False)
            
            msg = (
                f"A new version of {GAME_NAME} is available!\n\n"
                f"Current version: {VERSION}\n"
                f"Latest version: {latest_version}\n\n"
                "Would you like to download and install the update now?"
            )
            
            with wx.MessageDialog(
                None, msg, "Update Available", wx.YES_NO | wx.ICON_INFORMATION
            ) as dlg:
                if dlg.ShowModal() == wx.ID_YES:
                    # Run updater.bat and exit
                    try:
                        # Use Popen to launch it detached
                        if sys.platform == "win32":
                            subprocess.Popen(["updater.bat"], shell=True)
                        else:
                            # Fallback for other platforms if needed, but project is Windows-focused
                            subprocess.Popen(["sh", "updater.sh"])
                        
                        sys.exit(0)
                    except Exception as e:
                        wx.MessageBox(f"Failed to start updater: {e}", "Error", wx.OK | wx.ICON_ERROR)
    except Exception as e:
        # Silently fail or log update check errors
        print(f"Update check failed: {e}")
