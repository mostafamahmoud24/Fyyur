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
from datetime import date
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db.init_app(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(1500))
    artists = db.relationship('Artist', secondary='Shows')
    shows = db.relationship('Show', backref=('Venues'),
                            cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.shows}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(150))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String(120)))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(1500))
    venues = db.relationship('Venue', secondary='Shows')
    shows = db.relationship('Show', backref=('Artists'), cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Artist {self.id} {self.name} {self.city} {self.state} >'


class Show(db.Model):
    __tablename__ = 'Shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    venue = db.relationship('Venue')
    artist = db.relationship('Artist')

    def __repr__(self):
        return f'<Show {self.id} {self.artist_id} {self.venue_id} {self.start_time}>'


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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  locations = []
  for venue in venues:
    if not {"city": venue.city, "state": venue.state} in locations:
      locations.append({"city": venue.city, "state": venue.state})

  data = []

  for location in locations:
    locationVenues = []
    for venue in venues:
      upcoming_shows = 0
      shows = Show.query.filter_by(venue_id=venue.id).all()
      for show in shows:
        if show.start_time > datetime.now():
          upcoming_shows += 1

      if venue.city == location['city'] and venue.state == location['state']:
        locationVenues.append({"id": venue.id,"name": venue.name,"num_upcoming_shows": upcoming_shows,})

    data.append({"city": location['city'],
      "state": location['state'], "venues": locationVenues})
        
      
      

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  result = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  response = {
    'count': len(result),
    'data': result
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
  venues = Venue.query.all()
  venue_data = []
  for venue in venues:
    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0
    new_data_venue = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
    }
    for show in venue.shows:
      if show.start_time <= datetime.now():
        past_shows.append({
          "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
        })
        new_data_venue['past_shows_count'] += 1
      else:
        upcoming_shows.append({
          "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
        })
        new_data_venue['upcoming_shows_count'] += 1
    venue_data.append(new_data_venue)

  data = list(filter(lambda d: d['id'] == venue_id, venue_data))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website = request.form.get('website')
  seeking_talent = request.form.get('seeking_talent')
  seeking_description = request.form.get('seeking_description')

  if seeking_talent == 'y':
    seeking_talent = True
  else:
    seeking_talent = False

  try:
    new_venue = Venue(
      name=name, 
      city=city, 
      state=state, 
      address=address,
      phone=phone,
      genres=genres,
      facebook_link=facebook_link,
      image_link=image_link,
      website=website,
      seeking_talent=seeking_talent,
      seeking_description=seeking_description
    )
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + name + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + name + ' could not be listed.')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    db.session.delete(venue)
    db.session.commit()
    flash("Venue deleted Successfully")
  except:
    flash("Error occurred, unable to delete venue" + venue.id)

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  result = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  response = {
    'count': len(result),
    'data': result
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artists = Artist.query.all()
  artist_data = []
  for artist in artists:
    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0
    new_data_artist = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
    }
    for show in artist.shows:
      if show.start_time <= datetime.now():
        past_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        })
        new_data_artist['past_shows_count'] += 1
      else:
        upcoming_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        })
        new_data_artist['past_shows_count'] += 1
    artist_data.append(new_data_artist)
    print(artist_data[0]['genres'])

  data = list(filter(lambda d: d['id'] == artist_id, artist_data))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website = request.form.get('website')
  seeking_venue = request.form.get('seeking_venue')
  seeking_description = request.form.get('seeking_description')

  if seeking_venue == 'y':
    seeking_venue = True
  else:
    seeking_venue = False

  try:
    venue = Artist.query.filter_by(id=artist_id).update(dict(
    name=name, 
    city=city, 
    state=state, 
    phone=phone,
    genres=genres,
    facebook_link=facebook_link,
    image_link=image_link,
    website=website,
    seeking_venue=seeking_venue,
    seeking_description=seeking_description))
    
    db.session.commit()
    flash('Artist ' + name + ' was successfully Edited!')
  except Exception as e:
    print(e)
    flash('An error occurred. Artist ' + name + ' could not be Edited.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website = request.form.get('website')
  seeking_talent = request.form.get('seeking_talent')
  seeking_description = request.form.get('seeking_description')

  if seeking_talent == 'y':
    seeking_talent = True
  else:
    seeking_talent = False

  try:
    venue = Venue.query.filter_by(id=venue_id).update(dict(
    name=name, 
    city=city, 
    state=state, 
    address=address,
    phone=phone,
    genres=genres,
    facebook_link=facebook_link,
    image_link=image_link,
    website=website,
    seeking_talent=seeking_talent,
    seeking_description=seeking_description))
    
    db.session.commit()
    flash('Venue ' + name + ' was successfully Edited!')
  except Exception as e:
    print(e)
    flash('An error occurred. Venue ' + name + ' could not be Edited.')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website = request.form.get('website')
  seeking_venue = request.form.get('seeking_venue')
  seeking_description = request.form.get('seeking_description')


  if seeking_venue == 'y':
    seeking_venue = True
  else:
    seeking_venue = False

  try:
    new_artist = Artist(
      name=name, 
      city=city, 
      state=state,
      phone=phone,
      genres=genres,
      facebook_link=facebook_link,
      image_link=image_link,
      website=website,
      seeking_venue=seeking_venue,
      seeking_description=seeking_description
    )
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + name + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + name + ' could not be listed.')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)
  })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')

  if artist_id == '' or venue_id == '' or start_time == '':
    flash('An error occurred. Show could not be listed.')
  else:
    validated = True

    venues = Venue.query.all()
    artists = Artist.query.all()
    shows = Show.query.first()

    for venue in venues:
      if int(venue_id) == int(venue.id):
        validated = True
        break
      else: 
        validated = False


    for artist in artists:
      if int(artist_id) == int(artist.id):
        validated = True
        break
      else: 
        validated = False

    try:
      if validated:
        newShow = Show(artist_id=int(artist_id), venue_id=int(venue_id), start_time=str(start_time))
        db.session.add(newShow)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
      flash('An error occurred. Show could not be listed.')
      
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)]')
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
