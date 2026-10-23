KRATOS ONLY - 0.11.9

A single mod for God of War Ragnarok (PC / Windows x64).
Skips all seven playable Atreus segments while keeping Kratos:
- Sneaking Out
- Ironwood
- First visit to Asgard
- Hel invasion
- Niflheim
- Bear segment during the war in Asgard
- Epilogue

Version 0.11.9 adds a Helheim access repair after the Hel invasion skip.
Once the Kratos/Atreus reunion scene is complete, it enables the Helheim
realm entry and the HEL_GARM050_FT arrival gateway if either is missing.
The same check runs when the exterior of Sindri's house loads, allowing
existing saves past this point to recover access. Load your save and
return to the outside of Sindri's house, then check the Mystic Gateway.
The repair does not complete quests or unlock other Helheim locations.
Offline checks passed; in-game confirmation of this repair is pending.

Version 0.11.8 fixed a possible installer crash when Windows command output
uses a different character encoding from Python (NoneType / lower error).
Process checks now read raw bytes and stop with a clear error if the check
fails. Version-output handling is also protected. Gameplay patches are
unchanged.

Version 0.11.7 replaced the Steam executable hash requirement with a numeric
file-version check. Supported executable version: 1.0.668.5700.
Executables with different hashes can now pass the version check, including
other store builds with the same numeric version. The quest database and all
16 patch targets must still match compatible game data. Non-Steam gameplay
has not been tested locally; the installer does not assume every store uses
identical assets or identical version metadata.
The 0.11.7 and 0.11.8 releases only changed the installer.

Version 0.11.6 added explicit cleanup of the Hel invasion's combat and rage
tutorial state when the reunion scene ends. It also prevents that scene's
rage hooks and repair callbacks from affecting later gameplay. This targets
the reported issue where enemies move and react but do not attack Kratos or
Atreus during the second Vanaheim visit. Gameplay confirmation is pending.
All previous skips and companion corrections are included.

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
To update, Uninstall older versions using their original installer before updating. Then run the new Install.cmd

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

The mod does not edit save files. It contains no save files, unrelated mod
DLLs or complete game assets. Patches are applied to your own game files.


