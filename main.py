from flask import Flask, redirect, url_for, render_template, request
import csv
import random
import requests
import urllib3

app = Flask(__name__)
app.static_folder='static'

# YOUR KEY HERE
api_key = 'KEY'

with open('netflix_titles.csv') as net:
        reader = csv.reader(net)
        rows = list(reader)
movies, tv = [], []
# Split the list --> movies, tv shows
for curr in rows:
    if (curr[1] == 'Movie'):
        if (curr[8] != 'NC-17' and curr[5] == 'United States'):
            movies.append(curr)
    else:
        tv.append(curr)

@app.route("/", methods=['GET', 'POST'])
def home():
    selection = []
    findMovies, findTV = 'movies' in request.form.getlist('options'), 'tv' in request.form.getlist('options')
   
    if findMovies and findTV:
        selection = rows
    else:
        selection = tv if findTV and not findMovies else movies
    choice = pickTitle(selection)

    # Retrieve info from TMDB database
    query = choice['name'].replace(' ', '%20')
    query_type = 'movie' if choice['type'] == 'Movie' else 'tv'
    url = f'https://api.themoviedb.org/3/search/{query_type}?api_key={api_key}&language=en-US&query={query}&page=1&include_adult=false'
    response = requests.request('GET', url)
    data = response.json()

    # Checks if selected movie is not in TMDB database (edge case)
    while ('results' not in data or not data['results']):
        choice = pickTitle(selection)
        data = getData(choice['name'])
    data = data['results'][0]

    # Retrieves poster from TMDB
    poster_url = f"http://image.tmdb.org/t/p/original{data['poster_path']}"
    choice['poster'] = poster_url
    return render_template("index.html", choice=choice)

@app.route("/about")
def about():
    return "Hello it is me!"

@app.route("/admin")
def admin():
    return redirect(url_for("home"))

def pickTitle(selection):
 # Choose a movie and convert to dictionary
    choice = random.choice(selection)
    choice = {
        'link' : f"http://netflix.com/watch/{choice[0]}",
        'type' : choice[1],
        'name' : choice[2],
        'director' : choice[3],
        'cast' : choice[4],
        'country' : choice[5],
        'year' : choice[7],
        'rating' : choice[8],
        'duration' : choice[9],
        'genre' : choice[10],
        'description' : choice[11],
    }
    return choice

def getData(name):
    query = name.replace(' ', '%20')
    url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&language=en-US&query={query}&page=1&include_adult=false'
    response = requests.request('GET', url)
    return response.json()

if __name__ == "__main__":
    app.run()



