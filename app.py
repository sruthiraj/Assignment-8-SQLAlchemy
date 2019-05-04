import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

from dateutil.relativedelta import relativedelta
import datetime

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
    f"Available Routes:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/&ltstart&gt<br/>"
    f"/api/v1.0/&ltstart&gt/&ltend&gt<br/>"
  
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    results = session.query(Measurement.date, Measurement.prcp).all()
    precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        precipitation.append(prcp_dict)

    return jsonify({'Precipitation_List':precipitation})


@app.route("/api/v1.0/stations")
def stations():
    station_results = session.query(Station.id, Station.station, Station.name, Station.longitude, Station.latitude, Station.elevation).all()
    stations_list = {
        'stations': station_results
    }
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def temp_obs():
    recent_measurement = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = datetime.datetime.strptime(recent_measurement.date, '%Y-%m-%d').date()
    date_one_year_ago =  recent_date - relativedelta(years=1)

    result_temp = session.query(Measurement.date, Measurement.tobs)\
           .filter(Measurement.date > date_one_year_ago)\
           .order_by(Measurement.date).all()
    temperature = []
    for date, temp in result_temp:
        temp_2015 = {}
        temp_2015['date'] = date
        temp_2015['temp'] = temp
        temperature.append(temp_2015)
    
    return jsonify({'Temperature_List':temperature})


@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    result_vals = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date > start_date).all()

    for tmin, tavg, tmax in result_vals:
        val_dict = {}
       
        val_dict['tmin'] = tmin
        val_dict['tavg'] = tavg
        val_dict['tmax'] = tmax
      
    return jsonify(val_dict)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    result_vals_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()

    for tmin, tavg, tmax in result_vals_temps:
        val_dict_temps = {}

        val_dict_temps['tmin'] = tmin
        val_dict_temps['tavg'] = tavg
        val_dict_temps['tmax'] = tmax

    return jsonify(val_dict_temps)


if __name__ == '__main__':
    app.run(debug=True)