import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

base = automap_base()

base.prepare(autoload_with = engine)

measurement = base.classes.measurement

station = base.classes.station

session = Session(engine)

app = Flask(__name__)

#Start at the homepage.
#List all the available routes.
@app.route("/")
def welcome():
    return (f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format YYYY-MM-DD.</p>"
)

#Convert the query results from your precipitation analysis 
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    data = dict()
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #session.query(func.max(measurement.date)).first()
    precip = session.query(measurement.date, measurement.prcp).filter(measurement.date >= query_date).all()
    for x in precip:
        data[x[0]] = [x[1]]
    #Return the JSON representation of your dictionary.
    return jsonify(data)


#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stats = session.query(station.station).all()
    stat_results = list(np.ravel(stats))
    return jsonify(stat_results)

#Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rslts = session.query(measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= query_date).all()

    temps = list(np.ravel(rslts))
#Return a JSON list of temperature observations for the previous year.
    return jsonify (temps)

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature 
# for a specified start or start-end range.
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start= None, end = None):
    session = Session(engine)
    sel = [func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)]

    if not end:
        results = session.query(*sel).filter(measurement.date >= start).all()

        
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()

    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run()