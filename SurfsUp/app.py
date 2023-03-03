# import Dependencies
import numpy as np
import datetime as dt
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
# Base.prepare(engine, reflect=True)
Base.prepare(autoload_with=engine)


# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>"

    )
#########################################################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns precipitation data for the last year"""
#    * Query for the dates and precipitation observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#           * Return the json representation of your dictionary.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    end = last_year.date()
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= end).all()

    precipitation_df = pd.DataFrame(precipitation, columns=['date','precipitation'])
    return jsonify(precipitation_df.to_dict(orient='index'))
    
#########################################################################################
@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict(orient='index'))
#########################################################################################
@app.route("/api/v1.0/tobs")
def tobs():
#    * Query for the dates and temperature observations from the last year of the most-active station.
#           * Return the json representation of your dictionary.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    end = last_year.date()
    temperature = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= end).all()

    temperature_df = pd.DataFrame(temperature, columns=['date','temperature'])
    return jsonify(temperature_df.to_dict(orient='index'))

#########################################################################################
@app.route("/api/v1.0/<start>")
def trip1(start):

 # Returns the min, max, and average temperatures calculated from the given start date to the end of the dataset    
    end_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(end_date, "%Y-%m-%d") - dt.timedelta(days=365)
    start_date = last_year.date()
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################
@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):

  # Returns the min, max, and average temperatures calculated from the given start date to the given end date  
    end_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(end_date, "%Y-%m-%d") - dt.timedelta(days=365)
    start_date = last_year.date()
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date <= end_date).filter(Measurement.date >= start_date).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################
if __name__ == "__main__":
    app.run(debug=True)
