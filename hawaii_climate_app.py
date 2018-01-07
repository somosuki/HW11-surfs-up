#Dependencies
from flask import Flask, jsonify

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

from datetime import datetime

# Database Set up
engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect = True)

#Save measurement and stations class as 'Measurement' and 'Stations' respectively
Measurement = Base.classes.measurement
Stations = Base.classes.stations

session = Session(engine)

#### Set up Flask
app = Flask(__name__)

#home route
@app.route("/")
def home():
    return ("Hawaii Weather Data API<br/>"
    "/api/v1.0/precipitation<br/>"
    "/api/v1.0/stations<br/>"
    "/api/v1.0/tobs<br/>"
    "/api/v1.0/yyyy-mm-dd/<br/>"
    "/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/")

#function for prcp and temp data routes
def prcp_or_temps(choice):
    #create date range based on last date in database
    most_current = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = most_current[0]
    last_year = last_date.replace(year = (last_date.year - 1))
    last_year = last_year.strftime("%Y-%m-%d")
    #query
    one_year = session.query(Stations.name, Stations.station, Measurement.date, choice).filter(Stations.station == Measurement.station, Measurement.date > last_year).order_by(Measurement.date.desc()).all()
    #holder for complete dictionary to be returned
    choice_dict = {}
    # list for each station's data 
    record_list = []
    for x in range(1, len(one_year)):
        # create record for each station 
        record_dict = {"station_id": one_year[x-1][1], "station name": one_year[x-1][0], "station %s measure" % (choice): one_year[x-1][3]}
        record_list.append(record_dict)
        #if date changes record date, use as key, and use choice list as values, then dump choice list for next date
        if one_year[x-1][2] != one_year[x][2]:
            date_str =  one_year[x-1][2].strftime("%Y-%m-%d")
            choice_dict[date_str] = record_list
            record_list = []
        # if last record in query add it and append to choice list
        if x == (len(one_year)-1):
            record_dict = {"station_id": one_year[x][1], "station name": one_year[x][0], "station prcp measure": one_year[x][3]}
            record_list.append(record_dict)
            date_str =  one_year[x][2].strftime("%Y-%m-%d")
            choice_dict[date_str] = record_list
    return choice_dict

#precipition route
@app.route("/api/v1.0/precipitation")
def precip_json():
    #call prcp_or temps function with proper datapoint
    results = prcp_or_temps(Measurement.prcp)
    return jsonify(results)
   

#station route
@app.route("/api/v1.0/stations")
def stations():
    #list for station data
    stations_list = []
    #query
    stations = session.query(Stations.station, Stations.name, Stations.latitude, Stations.longitude, Stations.elevation).all()
    #create a dictionary for each station's info and append to list
    for station in stations:
        station_dict = {"station_id": station[0], "name": station[1], "latitude": station[2], "longitude": station[3], "elevation": station[4]}
        stations_list.append(station_dict)
    # return to user
    return jsonify(stations_list)
    
# temps route using function
@app.route("/api/v1.0/tobs")
def temps_json():
    #call prcp_or temps function with proper datapoint
    results = prcp_or_temps(Measurement.tobs)
    return jsonify(results)
    
#start date route
@app.route("/api/v1.0/<start_date>/")
def temp_stats(start_date):
    #query using start date
    temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).first()
    #create dictionary from result
    temps_dict1 = {"minimum temperuture": temps[0], "maximum temperature": temps[1], "average temperature": temps[2]}
    return jsonify(temps_dict1)

#start/end date route
@app.route("/api/v1.0/<start_date>/<end_date>/")
def temp_range(start_date, end_date):
    #query
    temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).first()
    #create dictionary from result
    temps_dict2 = {"TMIN": temps[0], "TMAX": temps[1], "TAVG": temps[2]}
    return jsonify(temps_dict2)

if __name__ == '__main__':
    app.run(debug=True)
