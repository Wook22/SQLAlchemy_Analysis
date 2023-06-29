# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, inspect, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all the available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Design a query to retrieve the last 12 months of precipitation data and plot the results

    # Calculate the date 1 year ago from the last data point in the database

    recent = session.query(measurement.date).\
        order_by(measurement.date.desc()).first()
    
    last = dt.date.fromisoformat(recent[0]) - dt.timedelta(days= 365)

    prcp = session.query(measurement.date, func.max(measurement.prcp)).\
        filter(measurement.date > last).\
        group_by(measurement.date).all()

    prcp_dic = []
    for i in prcp:
        row = {}
        row["date"] = i[0]
        row["prcp"] = i[1]
        prcp_dic.append(row)

    return jsonify(prcp_dic)



@app.route("/api/v1.0/stations")
def stations():
    # stations = session.query(station.name,station.station).\
    #     group_by(station.name),all()
    
    # station_dic = []
    # for i in stations:
    #     row = {}
    #     row["name"] = i[0]
    #     row["station"] = i[1]
    #     station_dic.append(row)

    # return jsonify(station_dic)
    
    # Query all stations
    results = session.query(station.station, station.name).all()

    # Convert the query results to a list of dictionaries
    station_list = [{"station": station, "name": name} for station, name in results]

    return jsonify(station_list)




@app.route("/api/v1.0/tobs")
def tobs():
    # recent = session.query(measurement.date).\
    #     order_by(measurement.date.desc()).first()
    
    # last = dt.date.fromisoformat(recent[0]) - dt.timedelta(days= 365)
    # temp = session.query(measurement.tobs).\
    #     filter(measurement.date >= last).\
    #     filter(measurement.station == 'USC00519281').all()

    # temp_dic = []
    # for result in temp:
    #     row = {}
    #     row["date"] = temp[0]
    #     row["tobs"] = temp[1]
    #     temp_dic.append(row)

    # return jsonify(temp_dic)
    
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    one_year_ago = dt.date.fromisoformat(last_date[0]) - dt.timedelta(days=365)

    # Query temperature observations for the most active station in the last 12 months
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in results]

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")

def calc_temps(start):
    # Query minimum, average, and maximum temperatures for dates greater than or equal to the start date
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()

    # Convert the query results to a list of dictionaries
    temp_list = [{"Minimum temperature": min_temp, "Average temperature": avg_temp, "Maximum temperature": max_temp}
                 for min_temp, avg_temp, max_temp in results]

    return jsonify(temp_list)


@app.route("/api/v1.0/<start>/<end>")

def calc_temps_range(start, end):
    # Query minimum, average, and maximum temperatures for the specified date range
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()

    # Convert the query results to a list of dictionaries
    temp_list = [{"Minimum temperature": min_temp, "Average temperature": avg_temp, "Maximum temperature": max_temp}
                 for min_temp, avg_temp, max_temp in results]

    return jsonify(temp_list)
    



if __name__ == '__main__':
    app.run(debug=True)