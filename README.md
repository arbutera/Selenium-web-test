# Web Browser Test

<p>Python script to extract files from dirs, sub dirs or URL, test them with the use of selenium web drivers, and write console log errors to a CSV with specified schema.</p>

## Selenium Web Driver Extensions

Selenium web driver extensions can be found bundled within the repository for IE11, Chrome and Edge. There is an option to add additional webdrivers beyond those mentioned but must be downloaded and identified in script.

**For more information on Selenium Web Drivers, visit the [Selenium Repository](https://github.com/SeleniumHQ)**


## Options

> Bold flag denotes the parameter is required

| Flag		| Option			| Description 																								| Default 	| Example 				|
| :---: 	| --- 				| --- 																										| :---: 	| :---: 		 		|
| **`-d`**	| **`--directory`**	| Directory to test, which will be appended to Dev server path at: `//ciwiis0d0013/...CSC/WebRoot/online/`	|    		| `Issue/Software/CED` 	|
| `-w`  	| `--web-driver`	| Comma seperated list of webdrivers to use for testing 													| `chrome`	| `chrome, ie, edge`	|
| **`-u`**	| **`--user`**		| User ID number appended to URL as a parameter to authenicate on live pages 								|    		| `997271` 				|
| `-i`  	| `--ignore`		| Comma seperated list of directories to ignore 															|  			| `IBUS, RED` 			|
| `-t`  	| `--timeDelay`		| Delay (in seconds) on page load for each page tested.		 												|    `0` 	| `1.5` 				|

## Running the script  

Example command to run (including all options): 
````
$ python app.py -d "Issue/Software/CED" -i "IBUS, RED" -w chrome -u "997271" -t 1.5
````
Simpler command to run (this tests the entire software form directory):
````
$ python app.py -d "Issue/Software" -u "997271"
````


## Supported Browser Status

As of this last commit, only chrome supports logging of console errors. Due to the way this script is currently written, specified browsers will run through the directory of specified pages, but only chrome will log a CSV file with errors. [See this post](https://stackoverflow.com/questions/53343666/selenium-capture-ie-and-edge-console-log) for details.
