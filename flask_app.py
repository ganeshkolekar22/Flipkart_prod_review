import os
from flask import Flask,render_template,request
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
import urllib.request

app = Flask(__name__)

@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homepage():
    return render_template('index.html')

@app.route('/back', methods=['GET'])
@cross_origin()
def allModels():
    return render_template('all_models.html')

@app.route('/price', methods=['GET'])
@cross_origin()
def searchProd():
    return render_template('searchProd.html')

@app.route('/review', methods=['POST','GET'])
def prod_review():
    return render_template('prod_review.html')

def basic_procc(search):
    flipkart_url = "https://www.flipkart.com/search?q=" + search
    uClient = urllib.request.urlopen(flipkart_url)
    print('url:', uClient)
    flipkart_page = uClient.read()
    uClient.close()
    html = bs(flipkart_page, 'html.parser')
    bigbox = html.find_all('div', {'class': 'bhgxx2 col-12-12'})
    del bigbox[0:3]
    return bigbox


@app.route('/models_price', methods=['POST','GET'])
@cross_origin()
def index():
    print("called")
    if request.method == 'POST':
        search = request.form['content'].replace(" ", "%20")
        try:
            bigbox = basic_procc(search);
            box = bigbox[0]
            models = []
            for pr in bigbox:
                name = pr.find_all('div', {'class': '_3wU53n'})
                prod_name = name[0].text
                price = pr.find_all('div', {'class': '_1vC4OE _2rQ-NK'})
                prod_price = price[0].text
                mydict = {'Name': prod_name, 'Price':prod_price}
                models.append(mydict)
                # print(models)
        except Exception as e:
            print("Exception: ",e)
        return render_template('results.html', models = models[0:(len(models) - 2)])

@app.route('/models_review', methods=['POST','GET'])
def reviews():
    if request.method == 'POST':
        try:
            search = request.form['content'].replace(" ", "%20")
            bigbox = basic_procc(search)
            box =bigbox[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html =bs(prodRes.text, 'html.parser')
            commentboxes =prod_html.find_all('div', {'class':'_3nrCtb'})
            review = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                except:
                    name = 'No Name'
                try:
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = 'No Rating'

                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'

                try:
                    comtag = commentbox.div.div.find_all('div', {'class':''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    print('Exception while creating dictionary: ',e)

                mydict = {'Product':search, 'Name':name, 'Rating':rating, 'Comment Head':commentHead,
                              'Comment':custComment}
                review.append(mydict)
            return render_template('reviews.html', reviews = review[0:(len(review) - 1)])
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
            return render_template('results.html')
    else:
        return render_template('index.html')

# port = int(os.getenv("PORT"))
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    # app.run(host='0.0.0.0', port=port)