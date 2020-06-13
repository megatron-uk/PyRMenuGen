#!/usr/bin/env python3

import settings

def dataScraperCCD(image_data, verbose):
	""" Extract disc data from a CloneCD image file """
	
	disc_data = {
		'title' : "",
		'region' : "",
		'version' : "",
		'number' : "",
		'date' : ""
	}
	
	f = open(image_data['dir'] + '/' +  image_data['filename'], "rb")
	
	found = False
	ccd_type = False
	
	####################################
	#
	# Check for the valid disc string
	#
	####################################
	for BASE in settings.CCD_BASES:
		f.seek(BASE[1], 0)
		text_bytes = f.read(15)
		try:
			s = text_bytes.decode('ascii')
		except Exception as e:
			s = text_bytes
		if s == settings.DISC_STRING:
			if verbose:
				print("--- ! [CCD type %s] %s @ %s" % (BASE[0], s, BASE[1]))
			found = True
			ccd_type = BASE[0]
		if found:
			if verbose > 1:
				# Print the full 512 byte header
				f.seek(BASE[1], 0)
				text_bytes = f.read(512)
				try:
					s = text_bytes.decode('ascii')
				except Exception as e:
					s = text_bytes
				print("--- [HEADER] <%s>" % s)
			break
	
	####################################
	#
	# Extract a disc title
	#
	####################################
	
	if found is False:
		f.close()
		return disc_data
	else:
		if ccd_type == 0:
			# Type '0' CCD files have the disc title at +96 bytes
			BASE_TITLE_OFFSET = 96
		elif ccd_type == 2:
			# Type '2' CCD files have the disc title at +96 bytes
			BASE_TITLE_OFFSET = 96
		else:
			# Type '1' CCD files have the disc title at +32 bytes
			BASE_TITLE_OFFSET = 32
	
		if verbose > 1:
			print("--- Searching for title @ 0x%X" % (BASE[1] + BASE_TITLE_OFFSET))
			
		f.seek(BASE[1] + BASE_TITLE_OFFSET, 0)
		text_bytes = f.read(settings.DISC_TITLE_SIZE)
		try:
			s = text_bytes.decode('ascii', "ignore").rstrip()
			disc_data['title'] = s
		except Exception as e:
			disc_data['title'] = text_bytes
			print("--- x [Disc Title] Unable to extract disc title")
			print(e)
		if verbose:
			print("--- ! [Disc Title] %s" % (s))
	
	####################################
	#
	# Extract a disc region
	#
	####################################
	if ccd_type in [0, 2]:
		if ccd_type == 0:
			# Type '0' CDI files have the disc region at +64 bytes
			BASE_REGION_OFFSET = 64
		if ccd_type == 2:
			# Type '2' CDI files have the disc region at +80 bytes
			BASE_REGION_OFFSET = 80
		
		if verbose > 1:
			print("--- Searching for region @ 0x%X" % (BASE[1] + BASE_REGION_OFFSET))
		
		f.seek(BASE[1] + BASE_REGION_OFFSET, 0)
		text_bytes = f.read(settings.DISC_REGION_SIZE)
		try:
			s = text_bytes.decode('ascii')
			disc_data['region'] = s
		except Exception as e:
			print("--- x [Disc Region] Unable to extract disc region")
		if verbose:
			print("--- ! [Disc Region] %s" % (s))
	else:
		# I don't know the offset for type 1 yet
		disc_data['region'] = ""
		if verbose:
			print("--- x [Disc Region] Not supported on this image type")
	
	####################################
	#
	# Extract a disc version
	#
	####################################
	if ccd_type in [0, 2]:
		# Both type 0 and type 2 have version at the same location
		BASE_VERSION_OFFSET = 42
		
		if verbose > 1:
			print("--- Searching for version @ 0x%X" % (BASE[1] + BASE_VERSION_OFFSET))
		
		f.seek(BASE[1] + BASE_VERSION_OFFSET, 0)		
		text_bytes = f.read(settings.DISC_VERSION_SIZE)
		try:
			s = text_bytes.decode('ascii', 'ignore').rstrip()
			disc_data['version'] = s
		except Exception as e:
			print("--- x [Disc Version] Unable to extract disc version")
		if verbose:
			print("--- ! [Disc Version] %s" % (s))
	else:
		# I don't know the offset for type 1 yet
		disc_data['version'] = ""
		if verbose:
			print("--- x [Disc Version] Not supported on this image type")
	
	####################################
	#
	# Extract a disc number
	#
	####################################
	if ccd_type == 0:
		# Type '0' CDI files have the disc number at +59 bytes
		BASE_NUMBER_OFFSET = 59
		
		if verbose > 1:
			print("--- Searching for disc number @ 0x%X" % (BASE[1] + BASE_NUMBER_OFFSET))
		
		f.seek(BASE[1] + BASE_NUMBER_OFFSET, 0)
		text_bytes = f.read(settings.DISC_NUMBER_SIZE)
		try:
			s = text_bytes.decode('ascii')
			disc_data['number'] = s
		except Exception as e:
			print("--- x [Disc Number] Unable to extract disc number")
		if verbose:
			print("--- ! [Disc Number] %s" % (s))
	else:
		# I don't know the offset for type 1 yet
		disc_data['number'] = ""
		if verbose:
			print("--- x [Disc Number] Not supported on this image type")
			
	f.close()
	
	# Return all found disc data
	return disc_data
