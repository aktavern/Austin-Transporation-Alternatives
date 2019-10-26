import os

import pandas as pd
import numpy as np
import pickle
from datetime import datetime as dt

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

# save reference to the tables
All_Vehicles = Base.classes.all_vehicles
Vehicles = Base.classes.vehicles
Hours = Base.classes.hours
Months = Base.classes.months
Counts = Base.classes.counts
Weather = Base.classes.weather

# create our session from Python to the DB
session = Session(engine)

#################################################
# Functions
#################################################

# FUNCTION TO QUERY THE DATABASE FOR WEATHER INFORMATION TO COMPLETE 
# THE DATA NEEDED FOR PREDICTIONS
def cleanup(form_data):
    
    # convert inputs to strings and return values from database
    date = str(form_data[2]) + "-" + str(form_data[1]) + "-" + str(form_data[0])
    hour = str(form_data[3])
    vehicle = str(form_data[4])
    sel = [
        All_Vehicles.day,
        All_Vehicles.day_of_week,
        All_Vehicles.month,
        All_Vehicles.year,
        All_Vehicles.hour,
        All_Vehicles.atemp,
        All_Vehicles.ahum,
        All_Vehicles.awind,
        All_Vehicles.prec,
        All_Vehicles.vehicle_encoded,
        All_Vehicles.hour_encoded,
        All_Vehicles.month_encoded
    ]
    query_results = db.session.query(*sel).filter(All_Vehicles.date == date, 
                                                All_Vehicles.hour == hour,
                                                All_Vehicles.vehicle_encoded == vehicle).all()

    # if query does not return any results, get averages for prediction
    if query_results == []:

        # get the day of week
        date = dt.strptime(date,'%Y-%m-%d')
        weekday = date.weekday()
        
        # get average weather data 
        sql = """
        select round(avg(atemp),0) AS atemp,
        round(avg(ahum),0) AS ahum,
        round(avg(awind),0) AS awind,
        round(avg(prec),0) AS prec
        from weather
        where day = %s and month = %s
        """
        # use pandas to query the database using the above query
        weather_query = pd.read_sql_query(sql,engine, params=[form_data[0],form_data[1]])
        # convery query results to a list of integers
        weather_query = weather_query.values[0].astype('int')

        # convert hour to hour encoded 
        if form_data[3] >= 0 and form_data[3] <= 3:
            hour = 0
        elif form_data[3] >= 4 and form_data[3] <= 7:
            hour = 1 
        elif form_data[3] >= 8 and form_data[3] <= 11:
            hour = 2
        elif form_data[3] >= 12 and form_data[3] <= 15:
            hour = 3 
        elif form_data[3] >= 16 and form_data[3] <= 19:
            hour = 4 
        else:
            hour = 5 

        # query the hour encoded table for prediction
        hour_query = (session.query(Hours.hour_encoded).filter(Hours.hour_encoded == hour).all())[0][0]

        if form_data[1] >= 1 and form_data[1] <= 3:
            month = 0
        elif form_data[1] >= 4 and form_data[1] <= 6:
            month = 1
        elif form_data[1] >= 7 and form_data[1] <= 9:
            month = 2
        else:
            month = 3
        
        # query the hour encoded table for prediction
        month_query = (session.query(Months.month_encoded).filter(Months.month_encoded == month).all())[0][0]

        # create a new list using results from queries above in
        # the order required for the prediction
        query_results = []
        query_results.append(form_data[0])
        query_results.append(weekday)
        query_results.append(form_data[1])
        query_results.append(form_data[2])
        query_results.append(form_data[3])
        query_results.append(weather_query[0])
        query_results.append(weather_query[1])
        query_results.append(weather_query[2])
        query_results.append(weather_query[3])
        query_results.append(form_data[4])
        query_results.append(hour_query)
        query_results.append(month_query)
    # if query does return results, just get those results
    else:
        query_results = query_results[0]
    
    return(query_results)


# FUNCTION TO PROCESS THE PREDICTION LIST THROUGH PICKLE
def prediction(to_predict_list):
    # make input the appropriate shape for pickle
    to_predict = np.array(to_predict_list).reshape(1,12)
    # open pickle model
    loaded_model = pickle.load(open("model.pkl","rb"))
    # run prediction and return value
    result = loaded_model.predict(to_predict)
    return result[0]

# FUNCTION TO RETURN A HUMAN READABLE COUNT RESULT
def encoded(predicted_result):
    # convert input to an integer
    result = int(predicted_result)
    # query database for result
    encoded_result = db.session.query(Counts.count_group).filter(Counts.count_encoded == result).all()
    # return a more human-readable result
    return str(encoded_result[0][0])

def variables(query_results):
    # query database for encoded variables and return human-readable format
    vehicle_encoded = (db.session.query(Vehicles.vehicle_type).filter(Vehicles.vehicle_encoded == query_results[9]).all()[0][0])
    hour_encoded = (db.session.query(Hours.hour_group).filter(Hours.hour_encoded == query_results[10]).all()[0][0])
    month_encoded = (db.session.query(Months.month_group).filter(Months.month_encoded == query_results[11]).all()[0][0])
    
    future_count = db.session.query(All_Vehicles.count).filter(All_Vehicles.day == query_results[0], 
                All_Vehicles.month == query_results[2], All_Vehicles.year == query_results[3]).all()
    
    if future_count == []:
        count = "None"
    else:
        count = (db.session.query(All_Vehicles.count).filter(All_Vehicles.day == query_results[0], 
            All_Vehicles.month == query_results[2], All_Vehicles.year == query_results[3],
            All_Vehicles.hour == query_results[4], All_Vehicles.vehicle_encoded == query_results[9]).all()[0][0])
    
    variables_list = []
    variables_list.append(vehicle_encoded)
    variables_list.append(hour_encoded)
    variables_list.append(month_encoded)
    variables_list.append(count)

    return variables_list


#################################################
# Flask Routes
#################################################

@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")

@app.route("/result", methods=['POST'])
def result():
    """Return the results from predictions."""
    if request.method == 'POST':
        # convert form data to a dictionary
        form_data = request.form.to_dict()
        # get only the values from the dictionary
        form_data = list(form_data.values())
        # convert values from strings to integers
        form_data = list(map(int, form_data))

    query_results = cleanup(form_data)
    variable_list = variables(query_results)
    to_predict_list = list(map(int,query_results))
    predicted_result = prediction(to_predict_list)
    encoded_result = encoded(predicted_result)
    
    return render_template("result.html", prediction = encoded_result,
    day = query_results[0], month = query_results[2], 
    year = query_results[3], hour = query_results[4],
    vehicletype = variable_list[0],dow=query_results[1],
    atemp=query_results[5],ahum=query_results[6],
    awind=query_results[7],prec=query_results[8],
    hourg = variable_list[1], monthg = variable_list[2],
    count = variable_list[3])


if __name__ == "__main__":
    app.run()
