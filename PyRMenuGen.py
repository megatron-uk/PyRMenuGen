#!/usr/bin/env python3

###########################################
#
# Scans a directory of SEGA Saturn image files and generates the
# LIST.INI file as used by RMENU or RMENUKAI/PSEUDO SATURN KAI
# to browse and load via the Rhea/Phoebe optical drive emulator
#
###########################################

import getopt
import os
import re
import sys
import shutil
import subprocess
import traceback

################################################
#
# Image-specific functions begin here
#
################################################

import settings
from cdi import dataScraperCDI
from ccd import dataScraperCCD	
from iso import dataScraperISO

###############################################################
#
# Main script code here - nothing disc-specific beyond this point
#
###############################################################

def title():
	print("%s	- RMENU list.ini and .iso generator for the SEGA Saturn" % __file__)
	print("		Rhea/Phoebe optical drive emulator")
	print("")

def help():
	""" Show command line use """

	title()
	print("Options:")
	print("-v --verbose 	Enable extra debug output")
	print("-d --dir	Directory where your Saturn images and ")
	print("		RMENU ./%s/ directory are located" % settings.RMENU_DIR)
	print("-s --scan	Scan directories and regenerate the LIST.INI file")
	print("-i --iso	Create the RMENU .iso file")
	print("-r --rename	Rename directories to the 001-999 standard")
	print("")
	print("Menu Options:")
	print("--menu-1	Use the traditional RMENU interface")
	print("--menu-2	Use the replacement Rmenu Kai interface")
	print("")
	print("e.g.")
	print("%s -d /mnt/sd_card -s" % __file__)
	print("")
	print("Scans the directories under /mnt/sd_card, generates a LIST.INI file")
	print("and drops it in to /mnt/sd_card/%s/BIN/RMENU" % settings.RMENU_DIR)
	print("")
	print("%s -d /mnt/sd_card -i" % __file__)
	print("")
	print("Use a pre-existing LIST.INI file found in /mnt/sd_card/%s/BIN/RMENU" % settings.RMENU_DIR)
	print("and generate the RMENU .iso file.")
	print("")
	print("%s -d /mnt/sd_card -s -i" % __file__)
	print("")
	print("All-in-one: scan the directories, generate the LIST.INI file and then")
	print("generate the RMENU .iso file.")
	
def decode_options():
	""" Parse command line options """
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "vhsird:", ["help", "verbose", "scan", "iso", "dir=", "menu-1", "menu-2", "rename"])
	except getopt.GetoptError as err:
		print(str(err))
		help()
		sys.exit(2)

	mode_rename = False
	mode_scan = False
	mode_iso = False
	data_dir = None
	verbose = False
	mode_menu = 1
	go = True
	
	for o, a in opts:
		if o in ("-v", "--verbose"):
			verbose = True
		elif o in ("-h", "--help"):
			help()
			sys.exit()
		elif o in ("-r", "--rename"):
			mode_rename = True
		elif o in ("-s", "--scan"):
			mode_scan = True
		elif o in ("-i", "--iso"):
			mode_iso = True
		elif o in ("-d", "--dir"):
			data_dir = a
		elif o in ("--menu-1"):
			mode_menu = 1
		elif o in ("--menu-2"):
			mode_menu = 2
		else:
			assert False, "unhandled option"

	# Check we've supplied a data dir
	if (data_dir is None):
		print("ERROR: You must set the data directory with the [dir] option")
		go = False

	# Check we've selected at least one of the modes
	if (mode_scan is False) and (mode_iso is False) and (mode_rename is False):
		print("ERROR: You must choose at least one of the [rename], [scan] or [iso] options")
		go = False
		
	if go is False:
		print("")
		print("%s -h for help and options" % __file__)
		sys.exit(2)
		
	#####################################
	#
	# A small banner about the selected options
	#
	#####################################
	print("")
	title()
	print("Dir:		%s" % data_dir)
	print("RMENU:		%s/%s/" % (data_dir, settings.RMENU_DIR))
	print("Scan mode:	%s" % mode_scan)
	print("ISO mode:	%s" % mode_iso)
	print("Menu type:	%s" % mode_menu)
	
	# Check that the directory actually exists
	print("")
	print("Checking data dir...")
	if (os.path.isdir(data_dir)):
		print("- OK")			
	else:
		print("- ERROR, data directory [%s] does not exist" % data_dir)
		sys.exit(2)
	
	# Verify that the RMENU folder is present
	print("")
	print("Checking for RMENU...")
	if os.path.isdir(data_dir + "/" + settings.RMENU_DIR + "/"):
		print("- Directory OK")
	else:
		print("- ERROR, RMENU directory [%s/%s/] does not exist" % (data_dir, settings.RMENU_DIR))
		sys.exit(2)
	
	# Check that all the RMENU files are present
	found = True
	for f in settings.RMENU_FILES:
		if os.path.isfile(data_dir + "/" + settings.RMENU_DIR + "/BIN/RMENU/" + f):
			pass
		else:
			print("- x %s/BIN/RMENU/%s - missing" % (settings.RMENU_DIR, f))
			found = False
	if found == False:
		print("- ERROR, One or more RMENU files are missing")
		sys.exit(2)
	else:
		print("- Files OK")
		
	##################################
	#
	# This is rename mode, any directories found that do
	# not conform with the 000-999 naming convention
	# will be renamed to the next available numbered
	# directory, including any spaces in the sequence.
	#
	##################################
	if mode_rename:
		print("")
		print("Finding non-conforming directory names...")
		dirnumbers = []
		for d in range(1, 99):
			d_name = "%02d" % d
			dirnumbers.append(d_name)
		for d in range(100, 999):
			d_name = "%03d" % d
			dirnumbers.append(d_name)	
		master_dirnumbers = dirnumbers.copy()
		
		dirs = os.listdir(data_dir)
		dirs.sort()
		for d in dirs:
			# Remove any dirnumbers if they already exist in
			# the just-ran dir list
			dirnumbers = list(filter((d).__ne__, dirnumbers))
		
		rename_dirs = []
		for d in dirs:
			if d in master_dirnumbers:
				pass
			else:
				new_dirname = dirnumbers[0]
				dirnumbers.pop(0)
				src_dir = data_dir + "/" + d
				dst_dir  = data_dir + "/" + new_dirname
				rename_dirs.append((src_dir, dst_dir))
		
		for d in rename_dirs:
			shutil.move(d[0], d[1])
		print("- OK")
			
	##################################
	#
	# This is scan mode - we generate a new LIST.INI at the
	# end of this.
	#
	##################################
	if mode_scan:
	
		# Generate a list of valid directory names
		valid_subdirs = []
		for i in range(1,999):
			v = "%03d" % i
			valid_subdirs.append(v)
	
		##########################################
		#
		# Find first level subdirectories
		#
		##########################################
		dir_warnings = False
		print("")
		print("Finding subdirs...")
		data_sub_dirs_tuples = os.listdir(data_dir)
		data_sub_dirs = []
		for sd in data_sub_dirs_tuples:
			sd_name = sd
			# Strip just the directory name off the /really/long/path/where/it/is
			if '/' in sd_name:
				sd_name = sd_name.split('/')[-1]
			if sd_name in ['01', '', "..", ".", "/"]:
				# Don't record the RMENU directory itself
				pass
			else:
				# Add the subdir to the list
				if sd_name not in valid_subdirs:
					print("- WARNING, %s is not a valid directory name for Rhea/Phoebe" % sd_name)
					dir_warnings = True
				data_sub_dirs.append(sd_name)
		data_sub_dirs.sort()
		print("- %s subdirs found" % len(data_sub_dirs))
		
		if len(data_sub_dirs) == 0:
			print("- ERROR, no subdirs found")
			sys.exit(2)
			
		##########################################
		#
		# We have some subdirs to check, now look for valid image files...
		# .ccd, .cdi, .mdf, .iso
		#
		##########################################
		print("")
		print("Scanning for images...")
		image_files = []
		for sd in data_sub_dirs:
			full_sd_path = data_dir + "/" + sd
			sd_has_image = []
			
			# List all the files in this subdir
			files = os.listdir(full_sd_path)
			for f in files:
				i = {
					'dir' : full_sd_path,
					'subdir' : sd,
					'filename' : f,
					'is_cdi' : False,
					'is_ccd' : False,
					'is_mdf' : False,
					'is_iso' : False,
				}
				found = False
				
				# Match the filename against known (and supported) image types
				file_match = re.search(".cdi", f, re.IGNORECASE)
				if file_match:
					i['is_cdi'] = True
					found = True
				file_match = re.search(".img", f, re.IGNORECASE)
				if file_match:
					i['is_ccd'] = True
					found = True
				file_match = re.search(".mdf", f, re.IGNORECASE)
				if file_match:
					i['is_mdf'] = True
					found = True
				file_match = re.search(".iso", f, re.IGNORECASE)
				if file_match:
					i['is_iso'] = True
					found = True
					
				if found:
					#if verbose:
					#	print("- %s [cdi:%s, ccd:%s, mdf:%s, iso:%s]" % (i['filename'], i['is_cdi'], i['is_ccd'], i['is_mdf'], i['is_iso']))
					# save the data of this image filanem
					image_files.append(i)
					
					# record that this subdir has an image file
					sd_has_image.append(sd)				
					
					# If we found one matching image file, break from the loop for this subdir
					# we dont want to risk processing more images in the same folder
					break
					
			if sd in sd_has_image:
				if verbose:
					print("- ! %s" % sd)
			else:
				print("- x %s [No valid image files found]" % sd)
		print("- %s image files found" % len(image_files))
		
		######################################
		#
		# For each image file, attempt to determine name of the game
		# version, data etc.
		#
		######################################
		print("")
		print("Extracting disc data...")
		images = []
		for i in image_files:
			image_data = None
			if verbose:
				print("")
				print("- %s" % i['filename'])
			if i['is_cdi']:
				image_data = dataScraperCDI(i, verbose)
			elif i['is_ccd']:
				image_data = dataScraperCCD(i, verbose)
			elif i['is_mdf']:
				image_data = dataScraperISO(i, verbose, is_mdf=True)
			elif i['is_iso']:
				image_data = dataScraperISO(i, verbose)
			else:
				pass
			if image_data:
				image_data['subdir'] = i['subdir']
				images.append(image_data)
		print("- %s image data records extracted" % len(images))
		
		# Now do the list
		print("")
		print("Generating LIST.INI")		
		if verbose:
			for i in images:
				#print("%s\r\n%s\r\n%s\r\n%s\r\n%s\r\n" % (i['title'], i['number'], i['region'], i['version'], i['date']))
				print("%s.title=%s" % (i['subdir'], i['title']))
				print("%s.disc=%s" % (i['subdir'], i['number']))
				print("%s.region=%s" % (i['subdir'], i['region']))
				print("%s.version=%s" % (i['subdir'], i['version']))
				print("%s.date=%s" % (i['subdir'], i['date']))
			
		# Write the data out to file
		f = open(data_dir + "/" + settings.RMENU_DIR + "/BIN/RMENU/" + settings.LIST_INI, "w")
		f.write("01.title=RMENU\r\n")
		f.write("01.disc=1/1\r\n")
		f.write("01.region=JTUE\r\n")
		f.write("01.version=v999\r\n")
		f.write("01.date=99999999\r\n")
		for i in images:
			f.write("%s.title=%s\r\n" % (i['subdir'], i['title']))
			f.write("%s.disc=%s\r\n" % (i['subdir'], i['number']))
			f.write("%s.region=%s\r\n" % (i['subdir'], i['region']))
			f.write("%s.version=%s\r\n" % (i['subdir'], i['version']))
			f.write("%s.date=%s\r\n" % (i['subdir'], i['date']))
		f.close()
		print("- OK")
		
		if dir_warnings:
			
			print("WARNING, ")
			print("WARNING, One or more of your game image directories is not stored in a folder in the range 000-999")
			print("WARNING, This is unlikely to work with Rhea/Saturn. You are advised to rename your folders to the")
			print("WARNING, standard naming convention of 01-99, 001-999 or 0001-9999.")
			print("WARNING, ")
			print("WARNING, The %s file will NOT be accurate (it uses indexed numbers to identify each image on the card)" % settings.LIST_INI)
		
			
	######################################
	#
	# This is ISO mode, we take an existing LIST.INI file and create
	# a new ISO file in the ./01/ subfolder by merging in the RMENU
	# binary files.
	#
	######################################
	if mode_iso:
		
		# Check that we have mkisofs
		print("")
		print("Checking for mkisofs...")
		if shutil.which(settings.MKISOFS):
			print("- OK")
		else:
			print("- ERROR, unable to find %s" % settings.MKISOFS)
			sys.exit(2)
			
		# Check that we have a LIST.INI
		print("")
		print("Checking for %s..." % settings.LIST_INI)
		if os.path.isfile(data_dir + "/" + settings.RMENU_DIR + "/BIN/RMENU/%s" % settings.LIST_INI):
			print("- OK")
		else:
			print("- ERROR, unable to find 01/BIN/RMENU/%s" % settings.LIST_INI)
			sys.exit(2)
		
		
		# Copy the correct menu file
		print("")
		print("Copying menu file...")
		if mode_menu == 1:
			src = data_dir + "/" + settings.RMENU_DIR + "/BIN/RMENU/" + settings.RMENU_BIN
		elif mode_menu == 2:
			src = data_dir + "/" + settings.RMENU_DIR + "/BIN/RMENU/" + settings.RMENUKAI_BIN
		else:
			print("- ERROR, invalid valid for menu file")
			sys.exit(2)
		shutil.copyfile(src, data_dir + "/" + settings.RMENU_DIR + "/BIN/RMENU/0.BIN")
		print("- Using %s" % src)
			
		# Create the ISO file using mkisofs
		cmd_dir = "cd '%s'; " % (data_dir + "/" + settings.RMENU_DIR + "/BIN/RMENU") 
		cmd = settings.MKISOFS
		cmd_args = """ -sysid 'SEGA SATURN' \
-V 'RMENU' \
-volset 'RMENU' \
-publisher 'SEGA ENTERPRISES, LTD.' \
-p 'SEGA ENTREPRISES, LTD.' \
-A 'RMENU' \
-abstract 'ABS.TXT' \
-copyright 'CPY.TXT' \
-biblio 'BIB.TXT' \
-G 'IP.BIN' \
-full-iso9660-filenames \
-input-charset 'iso8859-1' \
-o '%s/%s/RMENU.iso' '%s/%s/BIN/RMENU' """ % (data_dir, settings.RMENU_DIR, data_dir, settings.RMENU_DIR)
		print("")
		print("Going to run %s..." % settings.MKISOFS)
		print("- Running [%s %s]" % (cmd, cmd_args))
		os.system(cmd_dir + cmd + cmd_args)
	
		# We should check the iso has been created here
		# TODO
		
		# Any further checks...
	
if __name__ == "__main__":
    decode_options()