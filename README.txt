KRATOS ONLY - 0.11.8

A single mod for God of War Ragnarok (PC / Windows x64).
Skips all seven playable Atreus segments while keeping Kratos:
- Sneaking Out
- Ironwood
- First visit to Asgard
- Hel invasion
- Niflheim
- Bear segment during the war in Asgard
- Epilogue

Version 0.11.8 fixes a possible installer crash when Windows command output
uses a different character encoding from Python (NoneType / lower error).
Process checks now read raw bytes and stop with a clear error if the check
fails. Version-output handling is also protected. Gameplay patches are
unchanged.

INSTALLATION
1. Close the game.
2. Extract the KratosOnly folder from this ZIP into the game folder.
   The folder structure should be: [game folder]\KratosOnly\Install.cmd
   GoWR.exe must be one level above the KratosOnly folder.
3. Run Install.cmd and wait for the success message.
4. Start the game normally. Load a save from before the segment to skip.

No separate Python installation, dependency downloads or internet connection
are required. Do not run the installer directly from inside the ZIP.
If Windows denies access to the game folder, run Install.cmd as administrator.
Allow approximately 2 GB of free space for temporary files and backups.

UPDATING
To update, close the game and copy this package over
the existing KratosOnly folder. Keep the backups folder and
installation.json, then run Install.cmd.
Uninstall older versions using their original installer before updating.

UNINSTALLATION
Close the game and run KratosOnly\Uninstall.cmd.
Keep the KratosOnly folder, especially backups and installation.json. They
are created during installation and allow your exact original files to be
restored. Do not distribute these personal backups or the installation record.
To share the mod, distribute the original ZIP.

COMPATIBILITY AND GAMEPLAY NOTES
The installer reads GoWR.exe's fixed numeric file version using Windows
PowerShell. It does not launch the game or compare the complete executable
hash. The displayed FileVersion text may say 0,0,0,0; the numeric version used
by this package is 1.0.668.5700.
The quest database and each target file are verified before any game file is
changed. A matching executable version alone does not guarantee compatible
game data. Other game builds or mods that modify the same files may be
rejected. Compatibility with every game update is not guaranteed.
An unsupported-build error now includes both detected and supported numbers.
Do not bypass a quest-database or patch-target incompatibility error.
Saves already inside an Atreus segment may not trigger its skip.

After the Asgard bear skip, restart the checkpoint to restore the destroyed
scenery. Allow a few seconds after loading for companion recovery.
The 0.11.5 checkpoint recovery has passed offline checks; in-game validation
of this specific correction is still pending.

The mod does not edit save files. It contains no save files, unrelated mod
DLLs or complete game assets. Patches are applied to your own game files.

PACKAGE CONTENTS
Install.cmd / Uninstall.cmd: installation and restoration launchers.
install.py + patches.json.gz: installer and compressed patches.
runtime: bundled Python and LZ4, used only by the installer.
licenses: licenses for the included third-party components.

