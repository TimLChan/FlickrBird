Flickr Backup Tool
------------------

Download `flickrbird.py` to your Local Directory. 

Change `_userFlickr` value with your Flickr Photostream URL before running this script.
Add your `api_key` and `secret` from https://www.flickr.com/services/developer/api/

Run `python flickrbird.py` *or* `./flickrbird.py`

This will download all public photos to your current directory inside a folder denoted by the Flickr username you are trying to backup.


To-Do
------------------
- Add an option to read from cli instead of having to hardcode flickr photostream value

Changelog
------------------
0.2:

Updated to include API and Secret for Flickr API

Added support for multiple pages i.e. users with more than 500 photos

Added support to save to folders based on Flickr username
