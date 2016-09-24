#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       flickrbird.py
#
#       Copyright 2010 Abhinay Omkar <abhiomkar AT gmail DOT com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; Version 3 of the License
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, the license can be downloaded here:
#
#       http://www.gnu.org/licenses/gpl.html

# Meta
__version__ = '0.2'
__license__ = "GNU General Public License (GPL) Version 3"
__version_info__ = (0, 2)
__author__ = 'Abhinay Omkar <abhiomkar AT gmail DOT com>'
__maintainer__ = 'Tim Chan <tim AT timchan DOT com>'

#######################################################################################################################################################
# This script downloads Flickr User's public photos to current directory inside a folder denoted by the Flickr username you are trying to backup..
# Allows resuming download.
# Change the value of '_userFlickr' with the Flickr User's URL
# Change the value of '_photoSize' below
# Add your api_key and secret from your Flickr App Garden
#######################################################################################################################################################

import urllib, os, flickrapi

# Replace the below value with whatever URL of your Flickr photostream
_userFlickr = 'https://www.flickr.com/photos/photostreamhere'

# 's'	small square 75x75
# 't'	thumbnail, 100 on longest side
# 'm'	small, 240 on longest side
# ''	medium, 500 on longest side
# 'b'	large, 1024 on longest side (only exists for very large original images)
# 'o'	original image, either a jpg, gif or png, depending on source format (Pro Account Only)
_photoSize = 'o'

def main():
	global _photoSize
	api_key = ''
	secret = ''
	flickr = flickrapi.FlickrAPI(api_key, secret)
	
	# Convert Flickr URL to User NSID and get their username
	_userId = flickr.urls_lookupUser(url=_userFlickr).find('user').attrib['id']
	peopleUsername = flickr.people_getInfo(user_id=_userId).find('person/username').text
	
	# Get all user's public photos
	photos = []
	
	#Get number of pages
	numPages = flickr.people_getPublicPhotos(api_key=api_key, user_id = _userId, per_page = 500).find('photos').attrib['pages']
	
	#Where there is more than 1 page of photos, go through each page to get them all
	for i in range(1,int(numPages)+1):
		print "--> Getting page %s" % (str(i))
		publicPhotos = flickr.people_getPublicPhotos(api_key=api_key, user_id = _userId, per_page = 500, page = str(i))
		
		for photo in publicPhotos.getiterator('photo'):
			photos.append(photo.attrib['id'])

		totalPhotos=len(photos)
		flog = open('.'+_userId+'-photos','a+'); flog.seek(0); log = flog.read().split(';')

	#Create folder to house photos
	folder = os.path.join(os.getcwd(), peopleUsername)
	try: 
		os.makedirs(folder)
		print "--> Created folder %s" % str(folder)
	except OSError:
		print "--> Using folder %s" % str(folder)
		if not os.path.isdir(folder):
			raise
			
	# removing downloaded photos (log) from the download list (photos)
	photos = set([p+_photoSize for p in photos])-set(log)
	photos = [p.replace(_photoSize,'') for p in photos]
	if totalPhotos-len(photos):
		print "Skipping %s of %s photos. They are already downloaded." % (str(totalPhotos-len(photos)), str(totalPhotos))
	if len(photos)!=0:
		print "--> Started downloading %s photos" % str(len(photos))
	
	print '>> You can suspend the download with ^C.'
	
	# ok, start downloading photos one-by-one
	for photo in photos:
		photoTitle = flickr.photos_getInfo(photo_id=photo).find('photo/title').text or ''
		photoSizesTag = flickr.photos_getSizes(photo_id=photo).findall('sizes/size')
		photoSizes_list = [size.attrib['source'] for size in photoSizesTag]
		photoSizes = {}
		for size in photoSizes_list:
			if size[-6:-4] == '_s':
				photoSizes['square'] = size
			elif size[-6:-4] == '_t':
				photoSizes['thumbnail'] = size
			elif size[-6:-4] == '_m':
				photoSizes['small'] = size
			elif size[-6:-4] == '_b':
				photoSizes['large'] = size
			elif size[-6:-4] == '_o':
				photoSizes['original'] = size
			else:
				photoSizes['medium'] = size
	
		# .jpg ?
		photoType = photoSizes['square'][-4:]

		_photoSize = _photoSize.strip()
		if _photoSize == 's':
			photoDownload = photoSizes['square']
		elif _photoSize == 't':
			photoDownload = photoSizes['thumbnail']
		elif _photoSize == 'm' and photoSizes.has_key('small'):
			photoDownload = photoSizes['small']
		elif _photoSize == '' and photoSizes.has_key('medium'):
			photoDownload = photoSizes['medium']
		elif _photoSize == 'b' and photoSizes.has_key('large'):
			photoDownload = photoSizes['large']
		elif _photoSize == 'o':
			if photoSizes.has_key('original'):
				photoDownload = photoSizes['original']
			elif photoSizes.has_key('large'):
				photoDownload = photoSizes['large']
			elif photoSizes.has_key('medium'):
				photoDownload = photoSizes['medium']
			elif photoSizes.has_key('small'):
				photoDownload = photoSizes['small']
				
		print "Downloading: %s" % photoTitle
		# unix doesn't accept '/' in a file name, try $ touch 'foo/bar'
		photoTitle = photoTitle.replace('/','_')
		if photoTitle.startswith('.'):
		# The filename which starts with '.' is a hidden file
			photoTitle = photoTitle.replace('.', '_', 1)
		if _photoSize:
			photoSuffix = ''
		else:
			photoSuffix = '('+_photoSize+')'
		# actually, downloading now...
		urllib.urlretrieve(photoDownload, os.path.join(os.getcwd(), peopleUsername ,photoTitle+' '+str(photo)+' '+photoSuffix+photoType))
		flog.write(photo+_photoSize+';')

	
	if not peopleUsername:
	# Some times the Flickr user doesn't have a real name, so...
		peopleUsername = _userId
	print "--> Downloaded %s photos of %s !" % (str(len(photos)), peopleUsername)
	flog.close()
	# You have some awesome photos! :)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print "\n <-- Run it again to resume download. Bye!"