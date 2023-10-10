# sqlalchemy-challenge

# Climate Analysis and Exploration

This project involves climate analysis and data exploration of a climate database using SQLAlchemy ORM queries, Pandas, and Matplotlib.

## Technologies Used

- Python
- SQLAlchemy ORM
- SQLite
- Flask
- Pandas
- Matplotlib

## Database

The database used in this projectis `hawaii.sqlite`, which contains two tables: `Measurement` and `Station`.

## Analysis

The analysis includes:

1. Precipitation Analysis: A bar chart was plotted using the last 12 months of precipitation data.

2. Station Analysis: Calculations were made for the total number of stations, the most active station, and retrieving the last 12 months of temperature observation data (TOBSs).

3. Temperature Anaylsis: A function called `calc_temps` was used to accept a start date and end date in the format `%Y-%m-%d` and return the minimum, average, and maximum temperatures for that range of dates.

## Flask API

A Flask API was designed based on the queries developed. The following routes were created:

- `/`: Home page listing all available routes.
- `/api/v1.0/precipitation`: Returns a JSON representation of a dictoinary where the date is the key and the precipitation is the value.
- `/api/v1.0/stations`: Returns a JSON list of stations from the dataset.
- `/api/v1.0/tobs`: Returns a JSON list of temperature observations (TOBS) for the previous year.
- `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`: Returns a JSON list of minimum temperature, average temperature, and maximum temperaturer for a given start or start-end range.

