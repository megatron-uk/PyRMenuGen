# PyRMenuGen
A tool to generate a menu file as used by the Rhea/Phoebe optical drive emulator for the SEGA Saturn

## Status

  * Scanning and extraction of disc data for CloneCD (.img)
  * Scanning and extraction of disc data for and DiscJuggler (.cdi) - for several disc type variants
  * Scanning and extraction of disc data for Alcohol 120% (.mdf) - *Not yet implemented*
  * Scanning and extraction of disc data for iso/cue (.iso) - *Not yet implemented*
  * Generation of the RMENU `LIST.INI` file
  * Can choose to generate an original `RMENU ISO`, or `Rmenu Kai ISO` at runtime
  * Generates a bootable `ISO` file via a call to mkisofs

----

## Description

The SEGA Saturn has several optical drive emulators available; these replace the onboard CD-ROM drive with a modern SD card reader.

Although the hardware is great, there is no official menu interface available (though there are two third party menu systems available).

The RMENU system was developed first, and was a simple text based list of images as stored on the SD card. For the application to run a pre-built text file containing a list of all the titles has to be generated, built into an ISO file and started as the default image. The application itself has no direct way of reading the filesystem of the SD card.

Historically this was accomplished using a Windows based .exe tool that scanned a folder, built a menu file and then wrapped it in a bootable ISO image.

I wrote an alternative to this, for users on Linux or Mac OS systems, named https://github.com/megatron-uk/RheaMenu-Linux - this project is a direct replacement for that earlier tool.

----

## Useage

Mount the SD card that you are using. It should already have all of your Saturn images stored in numbered folders:

  * 01 to 99 - for up to 100 folders
  * 001 to 999 - for up to 1000 folders

Download all of the files in this project and run the main script PyRMenuGen.py:

`python3 PyRMenuGen.py`

Without any options it will display detailed command line argument help. There are basically two modes: scan and generate a new menu file and generate an ISO file from an existing menu file. You can combine the two into a single step, but you would most likely want to edit a menu file before creating the ISO.

First of all your SD card should have the original RMENU application unpacked to the '/01/' sub folder.

There are three possible scenarios at this point:

  * You are using [rmenu](https://gdemu.wordpress.com/links/) itself to select and load images
  * You are using the replacement [rmenu kai](https://ppcenter.webou.net/pskai/readme_rmenukai.txt) to select and load images
  * You are using [pseudo saturn kai](https://ppcenter.webou.net/pskai/) flashed to a cartridge to select and load images

### RMENU

If you have unzipped the standard release of RMENU to the './01/' sub directory, then all you need to do is rename the file `./01/BIN/RMENU/0.BIN` to `./01/BIN/RMENU/RMENU.BIN`. 

Simply scanning the directories (via the `--scan` option) and creating the iso (via the `--iso` option) will do everything needed for RMENU to work and create you a `RMENU.ISO` file in the `./01/` directory. Remove the SD card after this, pop it in the Rhea/Phoebe board in the Saturn and it should just work.

However.....

### Rmenu Kai

Rmenu Kai is a much improved menu system. It is installed over the top of an unpacked RMENU './01/' sub directory, and only involves copying in that projects `0.BIN` file TO `./01/BIN/RMENU/RMENUKAI.BIN` from the Rmenu Kai zip file.

*Note: Rmenu Kai names this file 0.BIN; I suggest it is renamed to RMENUKAI.BIN so that it and the original RMENU code can coexist together. PyRMenuGen can choose to build either at run-time.*

PyRMenuGen works exactly the same way after this, scanning folders and generating the ISO file. Removing the SD card and placing it in the Saturn should then load the alternative menu interface provided by Rmenu Kai instead of the old RMENU system.

But even better....

### Pseudo Saturn Kai

Pseudo Saturn Kai is replacement firmware for a number of Saturn cartridges. Pseudo Saturn Kai also uses either the RMENU or Rmenu Kai `ISO` file as generated for the two previous options.

Pseudo Saturn Kai has much more features than *just* launching images; cheat code support, save file exporting (if you have a cart that supports it), executable uploading etc. If you have an Action Replay cartridge you should **seriously** consider flashing it with Pseudo Saturn Kai firmware.

----

## Caveats

Depending on the method that was used to rip the original Saturn disc, you get varying degrees of accuracy and metadata from the image file.

The best quality rips I found come from images ripped using DiscJuggler or CloneCD with the all the options turned on:

  * Subcodes
  * Pre-gaps
  * CDI-G support

There are list of Saturn image files floating around the net, a lot of them are junk, especially those that have gone through multiple rip stages: original to bin/cue then to cdi/ccd for example.

Best quality is obtained by ripping discs yourself from originals, next best is finding a set from the various big-name dumps that have been imaged direct to CDI or CCD and **not** bin/cue.

----

## History
