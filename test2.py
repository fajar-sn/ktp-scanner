import win32com.client
oShell = win32com.client.Dispatch("Wscript.Shell")
print(oShell.SpecialFolders("Desktop"))