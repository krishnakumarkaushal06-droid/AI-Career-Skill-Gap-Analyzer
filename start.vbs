Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """" & WshShell.CurrentDirectory & "\RUN.BAT" & """", 0, False