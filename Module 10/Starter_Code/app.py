# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################

#1. ("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
    )

#2 .("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation data for the last year"""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    query_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d') - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).all()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    precip_data = {date: prcp for date, prcp in data}

    return jsonify(precip_data)

if __name__ == '__main__':
    app.run(debug=True)

#3 ("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

#4 ("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).\
        first()
    most_recent_date = session.query(Measurement.date).\
        filter(Measurement.station == most_active_station).\ 
    order_by(Measurement.date.desc()).\
        first()
    one_year_ago = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d') - dt.timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).\
        all()

    # Convert list of tuples into normal list
    temp_observations = list(np.ravel(results))

    return jsonify(temp_observations)

if __name__ == '__main__':
    app.run(debug=True)

#5 ("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the minimum temperature, the average temperature, and the maximum temperature for a given start
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Convert list of tuples into normal list
    temperatures = list(np.ravel(results))

    return jsonify(temperatures)

#6 ("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start-end range."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the minimum temperature, the average temperature, and the maximum temperature for a given start-end range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert list of tuples into normal list
    temperatures = list(np.ravel(results))

    return jsonify(temperatures)

if __name__ == '__main__':
    app.run(debug=True)