import os

import pandas as pd
import numpy as np
import pickle

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, render_template, request

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################

rds_connection_string = "postgres:Felicidad!1@localhost:5432/micromobility"
engine = create_engine(f'postgresql://{rds_connection_string}')
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f'postgresql://{rds_connection_string}')
db = SQLAlchemy(app)

# reflect existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# save reference to the table
Weather = Base.classes.weather

# create our session from Python to the DB
session = Session(engine)

#################################################
# Functions
#################################################

# function to process data using pickle model
def prediction(to_predict_list):
    # make input the appropriate shape for pickle
    to_predict = np.array(to_predict_list).reshape(1,12)
    # open pickle model
    loaded_model = pickle.load(open("model.pkl","rb"))
    # run prediction and return value
    result = loaded_model.predict(to_predict)
    return result[0]


#################################################
# Flask Routes
#################################################

@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")

@app.route("/result", methods=['POST'])
def result():
    if request.method == 'POST':
        # Convert form data to a dictionary
        to_predict_list = request.form.to_dict()
        # Get only the values from the dictionary
        to_predict_list = list(to_predict_list.values())
        # Convert values from strings to integers
        to_predict_list = list(map(int, to_predict_list))
        result = prediction(to_predict_list)

    # check weather and day of week
    date = str(to_predict_list[3]) + "-" + str(to_predict_list[2]) + "-" + str(to_predict_list[0])
    sel = [
        Weather.day_of_week,
        Weather.atemp,
        Weather.ahum,
        Weather.awind,
        Weather.prec,
    ]
    date_results = db.session.query(*sel).filter(Weather.date == date).all()
    print(date_results[0][0])

    # check vehicle type and grouped data 


    # Return different feedback based on value of result
    if int(result) == 0:
        demand = 'LITTLE DEMAND: Demand will be between 1 and 435.'
    elif int(result) == 1:
        demand = 'VERY, VERY SLIGHT DEMAND: Demand will be between 436 and 869'
    elif int(result) == 2:
        demand = 'VERY SLIGHT DEMAND: Demand will be between 870 and 1304'
    elif int(result) == 3:
        demand = 'SLIGHT DEMAND: Demand will be between 1305 and 1738'
    elif int(result) == 4:
        demand = 'MODERATE DEMAND: will be between 1739 and 2171'
    elif int(result) == 5:
        demand = 'SOMEWHAT SEVERE DEMAND: will be between 2172 and 2607'
    elif int(result) == 6:
        demand = 'SEVERE DEMAND: Demand will be between 2608 and 3011'
    elif int(result) == 7:
        demand = 'MORE SEVERE DEMAND:Demand will be between 3012 and 3476'
    elif int(result) == 8:
        demand = 'VERY SEVERE DEMAND: Demand will be between 3477 and 3892'
    elif int(result) == 9:
        demand = 'VERY, VERY SEVERE DEMAND: Demand will be between 3892 and 4334'
    else:
        demand = 'EXTREME DEMAND: Demand will be over 4335!'
    
    return render_template("result.html", prediction = demand,
        prediction_list = to_predict_list, date = date_results)

if __name__ == "__main__":
    app.run()
