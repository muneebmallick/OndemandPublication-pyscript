import getpass
import datetime
import requests
import gzip
import easywebdav
import os
from bs4 import BeautifulSoup as bs


user = raw_input("Username: ")
password = getpass.getpass()
date = raw_input("As of Date (mmddYYYY): ")

#add URL from where the files are required to be downloaded.
archive_url = 'URL'

def get_file_link():
	auth = ('user', 'pass')

	r = requests.get(archive_url, auth=auth, verify=False)

	soup = bs(r.content, 'html.parser')

	links = soup.findAll('a')

	file_links = [archive_url + link['href'] for link in links if date in link['href']] 

	return file_links



def download_big_file(url):
	auth = ('user', 'pass')
	local_filename = url.split('/')[-1]

	r = requests.get(url, stream=True, auth=auth, verify=False)
	with open(local_filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk:
				f.write(chunk)

	return local_filename


def download_file(url):
	auth = ('user', 'pass')

	files = []

	for link in url:
		local_filename = 'C:/TempFiles/' + link.split('/')[-1]
		with requests.session() as s:
			f = s.get(link, auth=auth, verify=False)

			with open(local_filename, 'wb') as g:
				g.write(f.content)
				g.close()
		files.append(local_filename)
	return files


def ungzip(files):

	filename = []

	for file in files:
		file_name = str(file.split('.')[0] + ".xml")
		with gzip.open(file, 'rb') as f:
			with open(file_name, 'wb') as u:
				u.write(f.read())

		os.remove(file)
		#Checking the file name for a specific word.
		if "MTM" in file:
			filename.insert(0,file_name)
		else:
			filename.append(file_name)	

	return filename


def copy_to_datafeed(file):

	webdav = easywebdav.connect(
	host = 'datafeeds.na.dir.mmallick.com',
	username = user,
	port = '443',
	protocol = 'https',
	password = password,
	verify_ssl = "C:/pyth/mmallick.pem")

	_file = '/pub-dev/' + file.split('/')[-1]

	webdav.upload(file, _file)


if __name__ == "__main__":

	print '\n' +"Downloading BAPI Links"+ '\n'
	bapi_links = get_file_link()
	# print bapi_links

	print '\n' + "Downloading Bapi Files" + '\n'
	gfiles = download_file(bapi_links)
	# print gfiles

	print '\n' + "Unzipping Bapi Files to a TEMP Location" + '\n'
	unfiles = ungzip(gfiles)
	# print unfiles

	print '\n' + "Copying Bapi Files to a pub-dev Data Feed Location" + '\n'
	for file in unfiles:
		copy_to_datafeed(file)
		os.remove(file)