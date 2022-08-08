# Download List 


Download files with pycurl using a list of urls; [Windows, Linux, Mac]

## Features
Multiprocessing, PyCurl


[**Download latest version (Windows)**](https://github.com/raylan-oliveira/dList/releases/latest)
## Demo:
![Demon](https://raw.githubusercontent.com/raylan-oliveira/dList/main/img/demo.gif)

### Dependencies
   ```sh
	pip install -r requeriments.txt
   ```
   
### Run
   ```sh
	python dList.py -f files_urls.txt
   ```
	
### Compile - Linux & Mac
   ```sh
	pip install pyinstaller
	pyinstaller dList.py --onefile	
   ```
### Compile - Windows | PyCurl Windows
Other versions of PyCurl for Windows: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycurl
   ```sh
	pip install pyinstaller
	python --version	
	cd pycurl_whl_windows_py_3.10
	pip install pycurl-7.45.1-cp310-cp310-win_amd64.whl # Python 3.10
   ```
### Usage
   ```sh
	usage: dlist [-h] -f FILE [-d DIRECTORY] [-p PATH] [-t THREAD]

    Download files with URL list

    options:
      -h, --help            show this help message and exit
      -f FILE, --file FILE  File with the URLs
      -d DIRECTORY, --directory DIRECTORY
                            Destination DIRECTORY; default='download_output'
      -p PATH, --path PATH  Keep the source PATH; default='false'
      -t THREAD, --thread THREAD
                            Thread number; default=50
