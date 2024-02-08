# Import the dependencies.
import pandas as pd
import numpy as np
import datetime as dt
# Get the dependencies we need for SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
# Add the code to import the dependencies that we need for Flask
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database into our classes.
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

# Default page with the details.
@app.route("/")
def welcome():
    return (
        f"<p>Welcome to the Hawaii weather API!</p>"
        f"<p>Usage Details:</p>"
        f"/api/v1.0/precipitation<br/>Returns a JSON list of percipitation data for the dates between 8/23/2016 and 8/23/2017<br/><br/>"
        f"/api/v1.0/stations<br/>Returns a JSON list of the stations<br/><br/>"
        f"/api/v1.0/tobs<br/>Returns a JSON list of the Temperature Observations (tobs) for each station for the dates between 8/23/2016 and 8/23/2017<br/><br/>"
        f"/api/v1.0/date<br/>Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between the given start date and 8/23/2017<br/><br/>."
        f"/api/v1.0/start_date/end_date<br/>Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between the given start date and end date<br/><br/>."
    )

# dates and precipitation observations from the last year in the dataset
@app.route('/api/v1.0/precipitation')
def precipitation():
    last_year_start = (dt.date(2017,8,23) - dt.timedelta(days=365)).isoformat()
    query = (f'SELECT date, prcp FROM measurement \
              WHERE date > "{last_year_start}"')
    return jsonify(pd.read_sql(query, engine).to_dict(orient='records'));

# json list of stations from the dataset.
@app.route('/api/v1.0/stations')
def stations():
    query = 'SELECT station, name FROM station'
    return jsonify(pd.read_sql(query, engine).to_dict(orient='records'));
 
# /api/v1.0/tobs
# Return a JSON list of Temperature Observations (tobs) for the previous year
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


# json list of the min temp, avg temp, max temp where date = given start<=
@app.route('/api/v1.0/')
def temps_startOnly(start):
    query = (f'SELECT AVG(temp) AS "Average Temperature", MIN(temp) \
                AS "Minimum Temperature", MAX(temp) AS "Maximum Temperature" \
                FROM measurement WHERE date >= "{start}"')
    return jsonify(pd.read_sql(query, engine).to_dict(orient='records'));

# json list: min temp, avg temp, max temp for dates between start/end inclusive
@app.route('/api/v1.0//')
def temps_startAndEnd(start, end):
    query = (f'SELECT AVG(temp) AS "Average Temperature", MIN(temp) \
               AS "Minimum Temperature", MAX(temp) AS "Maximum Temperature" \
               FROM measurement WHERE date >= "{start}" AND date <= "{end}"')
    return jsonify(pd.read_sql(query, engine).to_dict(orient='records'));  

#main class for Flask
if __name__ == "__main__":
    app.run(debug=True)