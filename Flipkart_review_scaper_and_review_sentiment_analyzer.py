# Import statements
from flask import Flask, render_template, url_for, request, redirect
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import MySQLdb
import mysql.connector
from mysql.connector import Error
from nltk.sentiment.vader import SentimentIntensityAnalyzer


import nltk
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # To retrive searched string from web form
        searchString = request.form['content']
        try:
            # Remove any whitespaces in 'searchString'
            searchString = searchString.replace(" ", "")
            # Connecting with MySQL Database
            connection = mysql.connector.connect(host="127.0.0.1",  user="root",  password="Sudeep!96",   database="crawlerDB")
            # Select query
            sql_select_Query = "select * from product_details where Product = %s"
            # Cursor object initialization for executing SQL query
            cursor = connection.cursor(buffered=True)
            # Executing SQL query
            cursor.execute(sql_select_Query, (searchString,))
            # If the records are already present in Database:
            if cursor.rowcount > 0:
                # Get the rows already present in Databse
                records = cursor.fetchall()
                reviews_list = []
                # Get the records from the database and create a dictionary to render the html page.
                for row in records:
                    # Sentence Analyzer function call
                    custComment_tag = sentiment_analyzer(row[4])
                    review_dict = {"Product": row[0], "Name": row[1], "Rating": row[2], "CommentHead": row[3],
                                   "Comment": row[4], "CommentTag": custComment_tag}

                reviews_list.append(review_dict)
                # render_template is used to convert a template into a complete HTML page
                return render_template('results.html',reviews=reviews_list)

            else:
                # Scrapping function call
                reviews_list = scrapper(searchString,connection)
                # render_template is used to convert a template into a complete HTML page
                return render_template('results.html', reviews=reviews_list)

        except Exception as e:
            # For Exception error message
            print('Failed : ' + str(e))
            return 'something is wrong'

    else:
        return render_template('index.html')



# Web scrapping function
def scrapper(searchString,connection):
    # Complete URL
    flipkart_url = "https://www.flipkart.com/search?q=" + searchString
    # To open given URL
    uClient = uReq(flipkart_url)
    # To read given URL page
    flipkartPage = uClient.read()
    uClient.close()
    # Parse the html page to extract the useful content using BeautifulSoup4
    flipkart_html = bs(flipkartPage, "html.parser")
    # Search for the link for the first product to redirect the product page.
    bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"})
    del bigboxes[0:3]
    box = bigboxes[0]
    #Parsing the product HTML page.
    productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
    prodRes = requests.get(productLink)
    prod_html = bs(prodRes.text, "html.parser")
    commentboxes = prod_html.find_all('div', {'class': "_3nrCtb"})

    reviews = []
    reviews_list = []
    # Iterating through every comment using 'div' tags and storing the required information
    for commentbox in commentboxes:
        try:
            name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text

        except:
            name = 'No Name'

        try:
            rating = commentbox.div.div.div.div.text
            rating = str(rating)

        except:
            rating = 'No Rating'

        try:
            commentHead = commentbox.div.div.div.p.text
        except:
            commentHead = 'No Comment Heading'
        try:
            comtag = commentbox.div.div.find_all('div', {'class': ''})
            custComment = comtag[0].div.text
        except:
            custComment = 'No Customer Comment'

        searchString = str(searchString)
        name = str(name)
        commentHead = str(commentHead)
        custComment = str(custComment)
        # Inserting scrapped rows into Database
        cursor = connection.cursor()
        # Insert query
        cursor.execute('INSERT INTO product_details (Product ,Name , Rating, CommentHead , Comment ) VALUES ("{}","{}","{}","{}","{}")'.format(searchString, name, rating, commentHead, custComment))
        # Commit the changes made in Database
        connection.commit()
        cursor.close()
        cursor = connection.cursor(buffered=True)
        # Select query to display the scrapped data
        sql_select_Query = "select * from product_details where product = %s"
        cursor.execute(sql_select_Query, (searchString,))
        reviews = cursor.fetchall()
        cursor.close()
        review_dict = {}
        for row in reviews:
            try:
                custComment_tag = sentiment_analyzer(row[4])
                review_dict = {"Product": row[0], "Name": row[1], "Rating": row[2], "CommentHead": row[3], "Comment": row[4], "CommentTag": custComment_tag}
            except:
                review_dict = {"Product": row[0], "Name": row[1], "Rating": row[2], "CommentHead": row[3],
                               "Comment": row[4], "CommentTag": "NA"}
        reviews_list.append(review_dict)
    print(reviews_list)
    print(len(reviews_list))
    return reviews_list


# Sentence analyzer function
def sentiment_analyzer(comment):
    comment_tag = sia.polarity_scores(comment)
    # For no reviews condition
    if comment == "No Customer Comment":
        return "NA"
    else:
        if comment_tag['compound'] > 0:
            return "Postive"
        else:
            return 'Negative'


if __name__ ==  "__main__":
    # app.run(host='127.0.0.1', port=8000)
    app.run(debug=True)

