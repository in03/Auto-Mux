@echo off
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\SendTo\Auto-Mux.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%cd%\Modules\Auto-Mux.cmd" >> CreateShortcut.vbs
echo oLink.IconLocation = "%cd%\Assets\Auto-Mux.ico" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%cd%\Modules\Auto-Mux.cmd" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs