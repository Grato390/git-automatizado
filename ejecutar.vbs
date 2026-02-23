Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
WshShell.CurrentDirectory = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.Run "cmd /c cd /d """ & WshShell.CurrentDirectory & """ && venv\Scripts\pythonw.exe git_automation_gui.py", 0, False
Set WshShell = Nothing
Set fso = Nothing
