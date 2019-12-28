# Flipkart-Review-Sentiment-Analysis
This project takes a product name as input and creates a review scraper from scratch, stores the scrapped data in MySQL database and then deploy it in a cloud environment.

Work Flow:
  1.	Take the input (E.g. mobile name) entered in the website. 
  2.	Check if the mobile name is existing in the database.
  3.	If existing, show the reviews to the user with Comments text sentiment analyzer.
  4.	If the mobile name is not existing, then scrap the reviews of that product from Flipkart website.
  5.	Then insert that product in Database.
  6.	Display the reviews with Comments text sentiment analyzer.

•	A HTML page is created to take the input from user using Flask, HTML and CSS.

•	MySQL is used for storing data.

•	For web scraping Python is used.

•	To perform Sentiment Analysis NLTK Analyzer is used.

•	Deployment is done using Heroku
