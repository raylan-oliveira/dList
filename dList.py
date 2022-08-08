from mime_types_formated import mime_type		
import requests									# pip install requests
import pycurl									# pip install pycurl

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import argparse
import re

from time import sleep

from os.path import exists
from os import mkdir
from urllib.parse import urlparse

def create_dir(nome_dir):
	nome_dir = clean_nome_dir(nome_dir)
	if exists(nome_dir) == False:
		mkdir(nome_dir)
		
def clean_nome_dir(string):
	string = re.sub(r'[^A-Za-z0-9-_ ./\\]', '_', string)
	return string

def clean_nome(string):
	string = re.sub(r'[^A-Za-z0-9-_ .]', '_', string)
	return string

# não baixar o mesmo arquivo duas vezes
list_all_nomes = []

def down_curl(url, full_file_name):	
	
	url_curl = False
	with open(full_file_name, "wb") as fp:
		curl = pycurl.Curl()
		curl.setopt(curl.URL, url)
		curl.setopt(curl.FOLLOWLOCATION, True)
		curl.setopt(curl.WRITEDATA, fp)
		curl.setopt(curl.USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36')
		try:
			curl.perform()
			code = curl.getinfo(curl.RESPONSE_CODE)
			url_curl = curl.getinfo(curl.EFFECTIVE_URL)		
			
			curl.close()
		except Exception as e:
			
			url_print = re.sub(r'\s+', '', url)
			
			msg = f'Curl download error: [{url_print}]' + '\n' +f'\t{e}'
			print(msg)
			try:
				with open('curl_downlaod_erros.txt', "a", encoding="utf-8") as downloads:
					line_write = msg + '\n'				
					
					downloads.write(line_write)
			except Exception as e:
				print(f'Error ao escrever a linha: [{line_write}]')
				print(f'\t{e}')	
				
			return 0
		
	return code

def func_dir_nome(dir_destination,url, path_source):
	
	url = re.sub(r'\s+', '', url)
	url_parse_all_info = urlparse(url)
	
	netloc = url_parse_all_info.netloc
	netloc = netloc.split(':')
	netloc = netloc[0]
	
	url_parse = url_parse_all_info
	file_name = url_parse.path.split('/')
	file_name = file_name[-1]
	
	if path_source:
		
		regex = re.compile(fr'{file_name}$')
		path_url = regex.sub('', url_parse.path)
		
		#path_url = path_url.replace('/', '\\')
		
		dir_destination = dir_destination + '/' + clean_nome_dir(netloc) + '/' + path_url
		
		old_folder = ''
		
		folders = dir_destination.split('/')
		
		for folder in folders:
			if folder == '':
				continue
			old_folder = old_folder + folder + '/'
			
			create_dir(old_folder)
	
	return dir_destination

def download_url(url, dir_destination, path_source):
	
	url = re.sub(r'\s+', '', url)
	url_parse = urlparse(url)
	
	file_name_e_extension = url_parse.path.split('/')
	file_name_e_extension = file_name_e_extension[-1]
	file_name_url = False
	file_extension_url = False
	
	file_name_url = re.sub(r'(.+?)(\.[A-Za-z0-9]+$)', '\g<1>', file_name_e_extension)
	if '.' in file_name_e_extension:
		file_extension_url = file_name_e_extension.split('.')
		file_extension_url = file_extension_url[-1]
	
	for tentativa in range(5):
		try:
			response = requests.get(url)
			break
		except Exception as e:
			print(f'Error requests: [{url}]')
			print(f'\t{e}')
			sleep(1)
	try:
		#text/html; charset=UTF-8
		extension_default = response.headers['Content-Type']
		
		#text/html
		extension_default = re.sub(r'(.+?)(\;.+?$)', '\g<1>', extension_default)		
		
		extension_mime = mime_type[extension_default]
		
		extension_mime_encontrada = False
		if len(extension_mime) >= 1:
			extension_mime_encontrada = True
			extension_default = extension_mime		
		
		if extension_mime_encontrada == False:
			#[text], [html]
			extension_default = extension_default.split('/')
			
			#html
			extension_default = extension_default[-1]
			
			extension_default = extension_default.lower()
			extension_default = extension_default.replace('+', '.')
			extension_default = extension_default.replace('-', '.')
			
		if file_name_e_extension == '' and extension_default == 'html':
			file_name_e_extension = 'index.html'		
		
		elif extension_default == 'html' or file_name_e_extension != '':			
			
			if file_extension_url == False or extension_default == 'html':
				
				file_name_e_extension = file_name_url + '.' + extension_default
			else:
				file_name_e_extension = file_name_url + '.' + file_extension_url
	except:
		pass
	
	if response.status_code >= 400:
		msg = f'{url} - [{response.status_code}]'
		print(msg)
		
		try:
			with open('erros_permission.txt', "a", encoding="utf-8") as downloads:
				line_write = msg + '\n'
				
				downloads.write(line_write)
		except Exception as e:
			print(f'Error writing line: [{line_write}]')
			print(f'\t{e}')	
		
		return
		
	url_curl = False
	# nomear file com o redirect
	if url != response.url:	
		
		dir_destination = func_dir_nome(dir_destination,response.url, path_source)
		
		url_curl = response.url
		url_curl = re.sub(r'\s+', '', url_curl)
		url_parse = urlparse(url_curl)
		
		file_name_e_extension = url_parse.path.split('/')
		file_name_e_extension = file_name_e_extension[-1]
		
		file_name_url = False
		file_extension_url = False
		
		file_name_url = re.sub(r'(.+?)(\.[A-Za-z0-9]+$)', '\g<1>', file_name_e_extension)
		
		if '.' in file_name_e_extension:
			file_extension_url = file_name_e_extension.split('.')
			file_extension_url = file_extension_url[-1]
		
		try:
			extension_redirect = response.headers['Content-Type']
			
			extension_redirect = re.sub(r'(.+?)(\;.+?$)', '\g<1>', extension_redirect)	
		
			extension_mime = mime_type[extension_redirect]
			extension_mime_encontrada = False
			
			if len(extension_mime) >= 1:
				extension_mime_encontrada = True
				extension_redirect = extension_mime		
			
			if extension_mime_encontrada == False:
			
				extension_redirect = extension_redirect.split('/')
				extension_redirect = extension_redirect[-1]
				extension_redirect = extension_redirect.lower()
				
				extension_redirect = extension_redirect.replace('+', '.')
				extension_redirect = extension_redirect.replace('-', '.')
				
			if file_name_e_extension == '' and extension_redirect == 'html':
				file_name_e_extension = 'index.html'
			
			elif extension_default == 'html' or file_name_e_extension != '':				
				if file_extension_url == False or extension_default == 'html':
					file_name_e_extension = file_name_url + '.' + extension_redirect
			
				else:
					file_name_e_extension = file_name_url + '.' + file_extension_url
			
		except:
			pass
				
	else:
		dir_destination = func_dir_nome(dir_destination,url, path_source)
	
	file_name_e_extension = clean_nome(file_name_e_extension)
	full_file_name = dir_destination + '/' + file_name_e_extension
	
	cont = 1
	if full_file_name in list_all_nomes or exists(full_file_name):
		# if path_source:
			# if 'index.html' not in full_file_name:
				# url_print = re.sub(r'\s+', '', url)
				# msg = f'{url_print}\n\t[{full_file_name}] já baixado...'
				# print(msg)
				
				# try:
					# with open('ja_baixados.txt', "a", encoding="utf-8") as downloads:
						# line_write = msg + '\n'
						
						# downloads.write(line_write)
				# except Exception as e:
					# print(f'Error ao escrever a linha: [{line_write}]')
					# print(f'\t{e}')	
			
				# return
		while True:
			print(f'Renaming: {full_file_name}')
			
			nome = re.sub(r'(.+?)(\.[A-Za-z0-9]+$)', '\g<1>', full_file_name)
			
			regex = re.compile(f'\_[0-9]+$')
			nome = regex.sub('', nome)
			
			nome = nome + '_' + str(cont)
			extension = '.html'
			
			if '.' in full_file_name:
				extension = full_file_name.split('.')
				extension = '.' + extension[-1]
				
							
				full_file_name = nome + extension			
			
			else:
				full_file_name = nome + extension
			
			cont += 1
			if exists(full_file_name) == False:
				if full_file_name not in list_all_nomes:
					print(f'\t=> {full_file_name}')
					#full_file_name = full_file_name.replace('\\\\', '\\')
					list_all_nomes.append(full_file_name)
					break
	
	else:
		list_all_nomes.append(full_file_name)
	
	code_return_curl = down_curl(url, full_file_name)
	if code_return_curl == 0 or code_return_curl >= 400:
		return	

	# se a primeira tentaiva do down__curl() não der certo, irá tentar mais 5 vezes...
	if exists(full_file_name) == False:
	
		for tentativa in range(5):
			print(f'Attempt: [{tentativa}] => {url}')
			
			code_return_curl = down_curl(url, full_file_name)
			if code_return_curl == 0:
				sleep(1)
				continue
			elif code_return_curl != 0:
				break
			
	#if exists(full_file_name) == True:
	retorno = f'{url} => {full_file_name} - [{code_return_curl}]'
	if url_curl:
		retorno = f'{url} => {url_curl} | => {full_file_name} - [{code_return_curl}]'
	print(retorno)
	line_write = retorno
	try:
		with open('downloads_files.txt', "a", encoding="utf-8") as downloads:
			line_write = f'{url} => {full_file_name} - [{code_return_curl}]\n'
			
			if url_curl:
				if url_curl != url:
					line_write =  f'{url} => {url_curl} | => {full_file_name} - [{code_return_curl}]\n'
				
			
			downloads.write(line_write)
	except Exception as e:
		print(f'Error writing line: [{line_write}]')
		print(f'\t{e}')
		
executor = ''
def run_executor(file_list_urls, num_thread, diretorio, path_source):
	
	with ThreadPoolExecutor(max_workers=num_thread) as executor:
		
		futures = []
		for url in file_list_urls:
			if re.search(r'^#', url) != None:
				# coment
				#print(f'Coment: [{url}]')
				continue
			elif re.search(r'^http', url) == None:
				
				url_print = re.sub(r'\s+', '', url)
				print(f'[http] not found in [{url_print}]')
				continue
			
				
			futures.append(executor.submit(download_url, url, diretorio, path_source))
		# for future in as_completed(futures):
			# if future.result() != 'Error':
				# print(future.result())

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Download files with URL list')
	parser.add_argument("-f", "--file", help='File with the URLs', required=True, type=str)
	parser.add_argument('-d', '--directory', help="Destination DIRECTORY; default='download_output'", required=False, type=str, default='download_output')
	parser.add_argument('-p','--path', help="Keep the source PATH; default='false'", default="false", type=str)
	parser.add_argument('-t', '--thread', help="Thread number; default=50", type=int, default=50)
	args = parser.parse_args()	
	
	create_dir(args.directory)
	try:
		file = open(args.file, "r", encoding='utf-8')
	except Exception as e:
		print(f'Error open file: [{args.file}]')
		print(f'\t{e}')
		exit()
	test_path = args.path.lower()
	if test_path == "true":
		run_executor(file, args.thread, args.directory, 'path')
	
	elif test_path == "false":
		pass
	else:
		print(f'[{test_path}] - incorrect...')
		exit()
	
		
	run_executor(file, args.thread, args.directory, None)