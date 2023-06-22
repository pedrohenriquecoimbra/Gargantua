Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "Gargantua-gui.bat" & Chr(34), 0
'WshShell.Popup "Opening OPEN FLUX.", 7, "Please wait", vbInformation
Set WshShell = Nothing
