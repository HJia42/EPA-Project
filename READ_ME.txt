READ_ME.txt

############ API ##########################################
****NOTE: after running "python manage.py runserver" from environment/, add "/project/" to the end of the url in your browser

Input a zip code in the U.S. (excluding Puerto Rico territories) and click 
"Find K". Inputting an invalid zip code will prompt you to re-enter a valid
zip code.

Code runs in theory but is taking too long :'(

If front-end does not load, can test what front end should look like by  uncommenting US_zips.py lines 61-62, then follow instructions in lineS 56 
and 103 of views.py

############ FRONTEND FILES ################################
Group_Project_2020/ : Group repository

environment/ : project directory name 
	environment/  
		settings.py
		urls.py : main url conf
	project/ : project app name
		views.py : views
		urls.py : url conf for project app
		templates/ : stores html templates
			base.html : homepage and base template
			about.html : about page
			results.html : results page
			team.html : meet the team page
			us_map.html : us_map page
	static/ : where css file is stored
		main.css

############### BACKEND FILES ###############################
environment/

	AQI_EPA.py: web scraping and data collection from AQI
	ECHO_db.py : web scraping and data collection from ECHO
				(ECHO server was down so we did not use the database, but included code for it that can be implemented at a later time)
	energy.py : web scraping and data collection from DOE
	weather.py : web scraping and data collection from 
	map.py : creating heat maps of the U.S. and the input state
	model_k.py : where K-model is created for a given input zip
	US_zips.py : creates pandas dfs of input zip code's scraped information, input
				zip state's scraped information, training and testing dfs, and categorizes location's urban noise and geographic region
	uszips.csv : csv file of all zip codes in the U.S.
	cd_2018_us_zcta510_500k.dbf, ^.shp, ^.shx : zip code map shape files
	st99_d00.dbf, ^.shp, ^.shx : continental U.S. map shape files
