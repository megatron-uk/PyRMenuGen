#!/usr/bin/env python3

import os.path
import settings

def dataScraperISO(image_data, verbose, is_mdf=False):
    """ Attempt to extract the disc name, version, date etc from a generic ISO or Alcohol 120% MDF image file """

    # MDF is headered, but can otherwise be handled the same
    if is_mdf:
        base = 16
    else:
        base = 0
    
    disc_data = {
        'title' : "",
        'region' : "",
        'version' : "",
        'number' : "",
        'date' : "",
    }
    
    f = open(os.path.join(image_data['dir'], image_data['filename']), "rb")
    f.seek(base, 0)

    text_bytes = f.read(15)
    try:
        s = text_bytes.decode('ascii')
    except Exception as e:
        s = text_bytes

    if s == settings.DISC_STRING:
        if verbose:
            if is_mdf:
                print("--- ! [MDF] %s @ %s" % (s, base))
            else:
                print("--- ! [ISO] %s @ %s" % (s, base))
        found = True

            
    ####################################
    #
    # Extract a disc title
    #
    ####################################
    if found is False:
        f.close()
        return disc_data
    else:
        f.seek(base + 96, 0)
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
    f.seek(base + 64, 0)
    text_bytes = f.read(settings.DISC_REGION_SIZE)
    try:
        s = text_bytes.decode('ascii')
        disc_data['region'] = s
    except Exception as e:
        print("--- x [Disc Region] Unable to extract disc region")
    if verbose:
        print("--- ! [Disc Region] %s" % (s))
    
    ####################################
    #
    # Extract a disc version
    #
    ####################################
    f.seek(base + 42, 0)
    text_bytes = f.read(settings.DISC_VERSION_SIZE)
    try:
        s = text_bytes.decode('ascii')
        disc_data['version'] = s
    except Exception as e:
        print("--- x [Disc Version] Unable to extract disc version")
    if verbose:
        print("--- ! [Disc Version] %s" % (s))
    
    ####################################
    #
    # Extract a disc date
    #
    ####################################
    f.seek(base + 48, 0)
    text_bytes = f.read(settings.DISC_DATE_SIZE)
    try:
        s = text_bytes.decode('ascii')
        disc_data['date'] = s
    except Exception as e:
        print("--- x [Disc Date] Unable to extract disc date")
    if verbose:
        print("--- ! [Disc Date] %s" % (s))
    
    ####################################
    #
    # Extract a disc number
    #
    ####################################
    f.seek(base + 59, 0)
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
