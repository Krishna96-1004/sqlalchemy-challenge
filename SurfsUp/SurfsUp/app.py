# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask,jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables
inspector = inspect(engine)
inspector.get_table_names()

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

# Find the most recent date in the data set.
Recent_date_set = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
Recent_date = dt.date.fromisoformat(Recent_date_set)

# Calculate the date one year from the last date in data set.
Last_TwelveMonths_date = dt.date(Recent_date.year-1,Recent_date.month,Recent_date.day)
Last_TwelveMonths_date

# Perform a query to retrieve the data and precipitation scores
precipitation_score = session.query(Measurement.date,func.max(Measurement.prcp)).\
    filter(Measurement.date >= func.strftime("%Y-%m-%d",Last_TwelveMonths_date)).\
    group_by(Measurement.date).\
    order_by(Measurement.date).all()

# Save the query results as a Pandas DataFrame and set the index to the date column
df = pd.DataFrame(precipitation_score, columns=['date', 'prcp'])
df.set_index('date', inplace=True)


# Use Pandas to calcualte the summary statistics for the precipitation data

precipitation_query = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= func.strftime("%Y-%m-%d",Last_TwelveMonths_date)).\
    order_by(Measurement.date).all()

df_ann_prcp = pd.DataFrame(precipitation_query, columns=['date', 'prcp'])
df_ann_prcp.set_index('date', inplace=True)
df_ann_prcp
precipitaion_df= df_ann_prcp.groupby(["date"]).max()["prcp"] 
min_precipitation = df_ann_prcp.groupby(["date"]).min()["prcp"] 
sum_precipitation = df_ann_prcp.groupby(["date"]).sum()["prcp"] 
precipitation_count = df_ann_prcp.groupby(["date"]).count()["prcp"] 

precipitation_dict= {"Max": precipitaion_df
                 ,"Min":min_precipitation
                 ,"Sum":sum_precipitation
                 ,"Count":precipitation_count 
                }

precipitation_summary_df = pd.DataFrame(precipitation_dict)
precipitation_summary_df

# Design a query to calculate the total number stations in the dataset
total_stations= session.query(Station.station).count()
total_stations
# Design a query to find the most active stations (i.e. what stations have the most rows?)
# List the stations and the counts in descending order.
most_active_stations_query = session.query(Measurement.station,func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc())

most_active_stations = most_active_stations_query.all()
most_active_stations

# Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
most_active_station_id = most_active_stations_query.first()[0]
most_active_station_id

temp_summ = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.station == most_active_station_id).all()

temp_summ

# Using the most active station id
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram

lastoneyear_temperatue_observation = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date >= func.strftime("%Y-%m-%d",Last_TwelveMonths_date), Measurement.station == most_active_station_id).\
    order_by(Measurement.date).all()

df_ann_tobs = pd.DataFrame(lastoneyear_temperatue_observation, columns=['date', 'tobs'])
df_ann_tobs.set_index('date', inplace=True)

qryStations = session.query(Station.station,Station.name, Station.latitude, Station.longitude, Station.elevation).all()
df_stations = pd.DataFrame(qryStations, columns=['station', 'name','latitude','longitude','elevation'])
df_stations.set_index('station', inplace=True) 

# Close Session
session.close()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
def index():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    result={}
    for index, row in precipitation_summary_df.iterrows():
        result[index]=dict(row)
    return jsonify(result) 

@app.route("/api/v1.0/stations")
def stations():
    result={}
    for index, row in df_stations.iterrows():
        result[index]=dict(row)
    return jsonify(result) 

@app.route("/api/v1.0/tobs")
def tobs():
    result={}
    for index, row in df_ann_tobs.iterrows():
        result[index]=dict(row)   
    return jsonify(result)
    
@app.route("/api/v1.0/<start>")
def fromstartdate(start):
    session = Session(engine)
    qry_fr_start_date = session.query(
            func.max(Measurement.tobs).label("TMAX"),
            func.avg(Measurement.tobs).label("TAVG"),
            func.min(Measurement.tobs).label("TMIN")
            ).\
        filter(Measurement.date >= start).all()

    df_fr_start_date = pd.DataFrame(qry_fr_start_date, columns=['TMAX', 'TAVG', 'TMIN'])
    result = df_fr_start_date.iloc[0].to_dict()

    session.close()
    return jsonify(result)

@app.route("/api/v1.0/<start>/<end>")
def fromrange(start,end):
    session = Session(engine)
    qry_fromrange = session.query(
            func.max(Measurement.tobs).label("TMAX"),
            func.avg(Measurement.tobs).label("TAVG"),
            func.min(Measurement.tobs).label("TMIN")
            ).\
        filter(Measurement.date >= start, Measurement.date <= end).all()

    df_fromrange = pd.DataFrame(qry_fromrange, columns=['TMAX', 'TAVG', 'TMIN'])
    result = df_fromrange.iloc[0].to_dict()

    session.close()
    return jsonify(result)

    return f"Start {start}? End: {end}"

if __name__ == "__main__":
    app.run(debug=True)