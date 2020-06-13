#!/usr/bin/env python3

import settings

def dataScraperCDI(image_data, verbose):
	""" Attempt to extract the disc name, version, date etc from a DiscJuggler .CDI image file """
	
	disc_data = {
		'title' : "",
		'region' : "",
		'version' : "",
		'number' : "",
		'date' : "",
	}
	
	f = open(image_data['dir'] + '/' +  image_data['filename'], "rb")
	
	found = False
	cdi_type = False
	
	####################################
	#
	# Check for the valid disc string
	#
	####################################
	for BASE in settings.CDI_BASES:
		f.seek(BASE[1], 0)
		text_bytes = f.read(15)
		try:
			s = text_bytes.decode('ascii')
		except Exception as e:
			s = text_bytes
		if s == settings.DISC_STRING:
			if verbose:
				print("--- ! [CDI type %s] %s @ %s" % (BASE[0], s, BASE[1]))
			found = True
			cdi_type = BASE[0]
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
		if cdi_type == 0:
			# Type '0' CDI files have the disc title at +96 bytes
			BASE_TITLE_OFFSET = 96
		else:
			# Type '1' CDI files have the disc title at +32 bytes
			BASE_TITLE_OFFSET = 32
			
		f.seek(BASE[1] + BASE_TITLE_OFFSET, 0)
		text_bytes = f.read(settings.DISC_TITLE_SIZE)
		try:
			s = text_bytes.decode('ascii').rstrip()
			disc_data['title'] = s
		except Exception as e:
			print("--- x [Disc Title] Unable to extract disc title")
		if verbose:
			print("--- ! [Disc Title] %s" % (s))
			
	####################################
	#
	# Extract a disc region
	#
	####################################
	if cdi_type == 0:
		# Type '0' CDI files have the disc region at +64 bytes
		BASE_REGION_OFFSET = 64
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
		# Type '1' CDI files dont appear to have region info (ripped from bin/cue)
		disc_data['region'] = ""
		if verbose:
			print("--- x [Disc Region] Not supported on this image type")
	
	####################################
	#
	# Extract a disc version
	#
	####################################
	if cdi_type == 0:
		# Type '0' CDI files have the disc region at +42 bytes
		BASE_VERSION_OFFSET = 42
		f.seek(BASE[1] + BASE_VERSION_OFFSET, 0)
		text_bytes = f.read(settings.DISC_VERSION_SIZE)
		try:
			s = text_bytes.decode('ascii')
			disc_data['version'] = s
		except Exception as e:
			print("--- x [Disc Version] Unable to extract disc version")
		if verbose:
			print("--- ! [Disc Version] %s" % (s))
	else:
		# Type '1' CDI files dont appear to have version info (ripped from bin/cue)
		disc_data['version'] = ""
		if verbose:
			print("--- x [Disc Version] Not supported on this image type")
	
	####################################
	#
	# Extract a disc date
	#
	####################################
	if cdi_type == 0:
		# Type '0' CDI files have the disc region at +48 bytes
		BASE_DATE_OFFSET = 48
		f.seek(BASE[1] + BASE_DATE_OFFSET, 0)
		text_bytes = f.read(settings.DISC_DATE_SIZE)
		try:
			s = text_bytes.decode('ascii')
			disc_data['date'] = s
		except Exception as e:
			print("--- x [Disc Date] Unable to extract disc date")
		if verbose:
			print("--- ! [Disc Date] %s" % (s))
	else:
		# Type '1' CDI files dont appear to have version info (ripped from bin/cue)
		disc_data['date'] = ""
		if verbose:
			print("--- x [Disc Date] Not supported on this image type")
	
	####################################
	#
	# Extract a disc number
	#
	####################################
	if cdi_type == 0:
		# Type '0' CDI files have the disc number at +59 bytes
		BASE_NUMBER_OFFSET = 59
	else:
		# Type '1' CDI files have the disc title at - 5 bytes
		BASE_NUMBER_OFFSET = -5
			
	f.seek(BASE[1] + BASE_NUMBER_OFFSET, 0)
	text_bytes = f.read(settings.DISC_NUMBER_SIZE)
	try:
		s = text_bytes.decode('ascii')
		disc_data['number'] = s
	except Exception as e:
		print("--- x [Disc Number] Unable to extract disc number")
	if verbose:
		print("--- ! [Disc Number] %s" % (s))
	
	f.close()
	
	# Return all found disc data
	return disc_data