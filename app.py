#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate, MigrateCommand
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database (Done)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description =db.Column(db.String)

    def format(self):
        return ({
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link
        })
    def get_by_id(id):
        return Venue.query.filter_by(id=id).first()

    def exhaustive_format(self):
        past_shows = past_show_venue(self.id)
        upcoming_shows = upcoming_show_venue(self.id)

        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
            'past_shows': [{
                'artist_id': show.artist_id,
                "artist_name": Artist.get_by_id(show.artist_id).name,
                "artist_image_link": Artist.get_by_id(show.artist_id).image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for show in past_shows],
            'upcoming_shows': [{
                'artist_id': show.artist.id,
                'artist_name': Artist.get_by_id(show.artist_id).name,
                'artist_image_link': Artist.get_by_id(show.artist_id).image_link,
                'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for show in upcoming_shows],
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        }

    # TODO: implement any missing fields, as a database migration using Flask-Migrate (Done)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    def format(self):
        return ({
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'genres': self.genres,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website_link': self.website_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description
        })

    def get_by_id(id):
        return Artist.query.filter_by(id=id).first()

    def exhaustive_format(self):
        past_shows = past_show_artist(self.id)
        upcoming_shows = upcoming_show_artist(self.id)

        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genres,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website_link,
            "facebook_link": self.facebook_link,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "past_shows": [{
              "venue_id": show.venue_id,
              "venue_name": Venue.get_by_id(show.venue_id).name,
              "venue_image_link": Venue.get_by_id(show.venue_id).image_link,
              "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for show in past_shows],
            "upcoming_shows": [{
                "venue_id": show.venue_id,
                "venue_name": Venue.get_by_id(show.venue_id).name,
                "venue_image_link": Venue.get_by_id(show.venue_id).image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for show in upcoming_shows],
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
        }

class Show(db.Model):
    __tablename__='Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist = db.relationship('Artist', backref=db.backref('shows',cascade="all,delete"))
    venue = db.relationship('Venue', backref=db.backref('shows', cascade="all,delete"))

    def format(self):
        return ({
            'id': self.id,
            'start_time': self.start_time,
            'artist_id': self.artist_id,
            'venue_id': self.venue_id,
        })

    def get_by_id(id):
        return Show.query.filter_by(id=id).first()

def past_show_venue(venue_id):
    past_shows = Show.query.filter(Show.start_time < datetime.datetime.now(),Show.venue_id==venue_id).all()
    return past_shows

def upcoming_show_venue(venue_id):
    upcoming_shows = Show.query.filter(Show.start_time > datetime.datetime.now(),Show.venue_id==venue_id).all()
    return upcoming_shows

def past_show_artist(artist_id):
    past_shows = Show.query.filter(Show.start_time < datetime.datetime.now(),Show.artist_id==artist_id).all()
    return past_shows

def upcoming_show_artist(artist_id):
    upcoming_shows = Show.query.filter(Show.start_time > datetime.datetime.now(),Show.artist_id==artist_id).all()
    return upcoming_shows

    # TODO: implement any missing fields, as a database migration using Flask-Migrate (Done)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. (Done)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  result = Venue.query.distinct(Venue.city, Venue.state).all()
  new_list = []
  new_dict = {}
  for item in result:
      new_dict["city"]=item.city
      new_dict["state"]=item.state
      new_list.append(new_dict)
      new_dict = {}

  for l in new_list:
      l["venues"]=[
      v.format() for v in Venue.query.filter_by(city=l["city"], state=l["state"]).all()
      ]
      # TODO: num_upcoming_shows ->
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  data = new_list
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')
  result = Venue.query.filter(Venue.name.like('%'+search_term+'%')).all()

  new_data = []
  new_dict = {}

  for item in result:
      new_dict["id"] = item.id
      new_dict["name"] = item.name
      new_data.append(new_dict)
      new_dict = {}

  new_response = {
    "count": len(result),
    "data": new_data
  }

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }

  response = new_response

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  result = Venue.query.filter_by(id=venue_id).all()
  data = result[0].exhaustive_format()
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)

  try:
      venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      )
      db.session.add(venue)
      db.session.commit()

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
      flash('Error occurred. Venue ' + form.name.data + ' could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
      venue = Venue.get_by_id(venue_id)
      db.session.delete(venue)
      db.session.commit()
      flash('The Venue has been successfully deleted!')
      return render_template('pages/home.html')
  except:
      db.session.rollback()
      flash('Delete was unsuccessful. Try again!')
  finally:
      db.session.close()
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  result = Artist.query.all()
  data = []
  new_dict = {}

  for item in result:
      new_dict["id"] = item.id
      new_dict["name"] = item.name
      data.append(new_dict)
      new_dict = {}

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term=request.form.get('search_term', '')
  result = Artist.query.filter(Artist.name.like('%'+search_term+'%')).all()

  new_data = []
  new_dict = {}

  for item in result:
      new_dict["id"] = item.id
      new_dict["name"] = item.name
      new_data.append(new_dict)
      new_dict = {}

  new_response = {
    "count": len(result),
    "data": new_data
  }

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  response = new_response
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  result = Artist.query.filter_by(id=artist_id).all()
  data = result[0].exhaustive_format()
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.get_by_id(artist_id)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    artist = Artist.get_by_id(artist_id)

    try:
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.facebook_link = form.facebook_link.data
        # TODO: deal with genre
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    except:
        db.session.rollback()
        flash('Error occurred. Artist ' + form.name.data + ' could not be edited.')
    finally:
        db.session.close()
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.get_by_id(venue_id)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm()
    venue = Venue.get_by_id(venue_id)

    try:
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.facebook_link = form.facebook_link.data
        # TODO: deal with genre
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
    except:
        db.session.rollback()
        flash('Error occurred. Venue ' + form.name.data + ' could not be edited.')
    finally:
        db.session.close()


  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  form = ArtistForm(request.form)

  try:
      artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      facebook_link = form.facebook_link.data,
      )
      db.session.add(artist)
      db.session.commit()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
      flash('Error occurred. Venue ' + form.name.data + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  result = Show.query.all()
  data = []
  new_dict = {}

  for item in result:
      new_dict["venue_id"] = item.venue_id
      new_dict["venue_name"] = Venue.get_by_id(item.venue_id).name
      new_dict["artist_id"] = item.artist_id
      new_dict["artist_name"] = Artist.get_by_id(item.artist_id).name
      new_dict["artist_image_link"] = Artist.get_by_id(item.artist_id).image_link
      new_dict["start_time"] = item.start_time.strftime("%m/%d/%Y, %H:%M")

      data.append(new_dict)
      new_dict = {}
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()

  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  try:
      show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time=form.start_time.data
      )
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed!')
  except:
      flash('Show could not be listed. Please try again')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
