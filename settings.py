#!/usr/bin/env python3

###########################################
#
# Configuration file for PyRMenuGen
#
###########################################

# Possible offsets (in bytes) where the SEGA disc data can be found...
# ... in DiscJuggler  .CDI files
# Type 0: proper, ripped full discs with all options ticked in DiscJuggler
# Type 1: usually converted bin/cue images without full disc headers
# Type 2 and 3 were reported here on my old shellscript based tool: https://github.com/megatron-uk/RheaMenu-Linux/issues/3
# Type 4 is a copy of Virtual Fighter Kids that came into my collection - I don't know why the offset differs again.
CDI_BASES = [(0, 352816), (1, 339976), (2, 367216), (3, 307200), (4, 339968)]

# ... and in CloneCD .IMG files
# Type 0 is the most common format, and the one which the bin/cue to ccd generator 'sbitools.exe' generates
# Type 1 I don't have any examples of
# Type 2 is what the Shining Force III patch utility generates 
CCD_BASES = [(0, 16), (1,112), (2,0)]

# ... and in Alchohol 120% .MDF files
MDF_BASES = []

# Valid discs should have this string
DISC_STRING = "SEGA SEGASATURN"
DISC_TITLE_SIZE = 32
DISC_REGION_SIZE = 10
DISC_VERSION_SIZE = 6
DISC_NUMBER_SIZE = 3
DISC_DATE_SIZE = 8

# List of files that should be in the RMENU folder under ./01/BIN/RMENU
RMENU_DIR = "01"
RMENU_BIN = "RMENU.BIN"
RMENUKAI_BIN = "RMENUKAI.BIN"
RMENU_FILES = ["0.BIN", "ABS.TXT", "BIB.TXT", "CPY.TXT", "IP.BIN", "Z.BIN"]
LIST_INI = "LIST.INI"

# Name of the mkisofs executable with which to create the RMENU ISO
MKISOFS = "mkisofs"
