import requests,time
import configparser
from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///weatherdb.sqlite'
db=SQLAlchemy(app)

class City(db.Model):
    city_name=db.Column(db.String(50),primary_key=True)


@app.route("/")
def index():
    #home page
    pinned_list=City.query.all()
    print(pinned_list)
    return render_template("index.html",pinned_list=pinned_list)

@app.route("/weather_details",methods=["POST"])
def weather_details():
    #call to receive json_data and actual extraction of data fron json object
    city_name=request.form['inputbox']
    api_key=get_api_key()
    json_data=get_data(city_name,api_key)
    try:
        name,country,description,temp,feels_like=extract_data(json_data)
        return render_template('details.html',name=name,country=country,description=description,temp=temp,feels_like=feels_like)
    except:
        return '<h1>Data not available</h1><h2>Enter a valid city name</h2><a href="/">Back</a>'

    
def get_api_key():
    config=configparser.ConfigParser()
    config.read("config.ini")
    api_key=config.get('openweathermap','api')
    return api_key


def get_data(city_name,api_key):
    #api_call 
    base_url="http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(city_name,api_key)
    resp=''
    while resp=='':
        try:
            resp=requests.get(base_url)
            print(base_url)
            break
        except:
            print(".............")
            time.sleep(5)
            continue
    return resp.json()

@app.route("/pin_city",methods=["POST"])
def pin_city():
    #add/pin custom cities
    city_name=request.form.get('pin')
    city_name=city_name.upper()
    city=City(city_name=city_name)
    db.session.add(city)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/pinned_details/<city_name>")
def get_pinned_details(city_name):
    #view weather details for pinned cities
    api_key=get_api_key()
    json_data=get_data(city_name,api_key)
    try:
        name,country,description,temp,feels_like=extract_data(json_data)
        return render_template('details.html',name=name,country=country,description=description,temp=temp,feels_like=feels_like)
    except:
        return '<h1>Data not available</h1><h2>Enter a valid city name</h2><a href="/">Back</a>'

@app.route("/delete_pinned/<city_name>")
def delete_pinned(city_name):
    #remove the pinned cities
    city=City.query.filter_by(city_name=city_name).first()
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for("index"))


def extract_data(json_data):    
    #extracting data from json object
    description=json_data['weather'][0]['main']
    temp=json_data['main']['temp']
    feels_like=json_data['main']['feels_like']
    name=json_data['name']
    country=json_data['sys']['country']
    return name,country,description,temp,feels_like
    

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)