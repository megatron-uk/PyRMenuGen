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
import traceback

################################################
#
# Image-specific functions begin here
#
################################################

import settings
from cdi import dataScraperCDI
from ccd import dataScraperCCD	

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
	print("-v --verbose 	Enable extra debug output")
	print("-d --dir	Directory where your Saturn images and ")
	print("		RMENU ./01/ directory are located")
	print("-s --scan	Scan directories and regenerate the LIST.INI file")
	print("-i --iso	Create the RMENU .iso file")
	print("")
	print("e.g.")
	print("%s -d /mnt/sd_card -s" % __file__)
	print("")
	print("Scans the directories under /mnt/sd_card, generates a LIST.INI file")
	print("and drops it in to /mnt/sd_card/01/BIN/.")
	print("")
	print("%s -d /mnt/sd_card -i" % __file__)
	print("")
	print("Use a pre-existing LIST.INI file found in /mnt/sd_card/01/BIN/")
	print("and generate the RMENU .iso file.")
	print("")
	print("%s -d /mnt/sd_card -s -i" % __file__)
	print("")
	print("All-in-one: scan the directories, generate the LIST.INI file and then")
	print("generate the RMENU .iso file.")
	
def decode_options():
	""" Parse command line options """
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "vhsid:", ["help", "verbose", "scan", "iso", "dir="])
	except getopt.GetoptError as err:
		print(str(err))
		help()
		sys.exit(2)

	mode_scan = False
	mode_iso = False
	data_dir = None
	verbose = False
	go = True
	
	for o, a in opts:
		if o in ("-v", "--verbose"):
			verbose = True
		elif o in ("-h", "--help"):
			help()
			sys.exit()
		elif o in ("-s", "--scan"):
			mode_scan = True
		elif o in ("-i", "--iso"):
			mode_iso = True
		elif o in ("-d", "--dir"):
			data_dir = a
		else:
			assert False, "unhandled option"

	# Check we've supplied a data dir
	if (data_dir is None):
		print("ERROR: You must set the data directory with the [dir] option")
		go = False

	# Check we've selected at least one of the modes
	if (mode_scan is False) and (mode_iso is False):
		print("ERROR: You must choose at least one of the [scan] or [iso] options")
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
	print("Scan mode:	%s" % mode_scan)
	print("ISO mode:	%s" % mode_iso)
	
	# Check that the directory actually exists
	print("")
	print("Checking data dir...")
	if (os.path.isdir(data_dir)):
		print("- OK")
	else:
		print("- ERROR, data directory [%s] does not exist" % data_dir)
		sys.exit(2)
	
	##################################
	#
	# This is scan mode - we generate a new LIST.INI at the
	# end of this.
	#
	##################################
	if mode_scan:
	
		##########################################
		#
		# Find first level subdirectories
		#
		##########################################
		print("")
		print("Finding subdirs...")
		data_sub_dirs_tuples = os.walk(data_dir)
		data_sub_dirs = []
		for sd in data_sub_dirs_tuples:
			sd_name = sd[0]
			# Strip just the directory name off the /really/long/path/where/it/is
			if '/' in sd_name:
				sd_name = sd_name.split('/')[-1]
			if sd_name in ['01', '', "..", ".", "/"]:
				# Don't record the RMENU directory itself
				pass
			else:
				# Add the subdir to the list
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
			full_sd_path = data_dir + sd
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
			#elif i['is_mdf']:
			#	image_data = dataScraperMDF(i, verbose)
			#elif i['is_iso']:
			#	image_data = dataScraperISO(i, verbose)
			else:
				pass
			if image_data:
				images.append(image_data)
		
		print("")
		print("- %s data extracted" % len(images))
		
		print("")
		print("Generating LIST.INI")
		c = 2
		for i in images:
			#print("%s\r\n%s\r\n%s\r\n%s\r\n%s\r\n" % (i['title'], i['number'], i['region'], i['version'], i['date']))
			print("%3s.title=%s" % (c, i['title']))
			print("%3s.disc=%s" % (c, i['number']))
			print("%3s.region=%s" % (c, i['region']))
			print("%3s.version=%s" % (c, i['version']))
			print("%3s.date=%s" % (c, i['date']))
			c += 1
			
	######################################
	#
	# This is ISO mode, we take an existing LIST.INI file and create
	# a new ISO file in the ./01/ subfolder by merging in the RMENU
	# binary files.
	#
	######################################
	if mode_iso:
		pass
	
if __name__ == "__main__":
    decode_options()