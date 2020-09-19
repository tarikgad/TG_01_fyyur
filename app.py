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
from flask_migrate import Migrate
from sqlalchemy import func,text
from enum import Enum
from datetime import datetime
import pytz
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

sh_art = db.Table('sh_art',
    db.Column('shows_id', db.Integer, db.ForeignKey('Shows.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)

sh_ven = db.Table('sh_ven',
    db.Column('shows_id', db.Integer, db.ForeignKey('Shows.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
)

class Shows(db.Model):
  __tablename__ = "Shows"
  id = db.Column(db.Integer, primary_key=True)
  artists = db.relationship('Artist', secondary=sh_art,backref=db.backref('shows', lazy=True))
  venues = db.relationship('Venue', secondary=sh_ven, backref=db.backref('shows', lazy=True))
  start_time = db.Column(db.DateTime(timezone=True), nullable=False)


class Venue(db.Model):
  __tablename__ = "Venue"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  city = db.Column(db.String(), nullable=False)
  state = db.Column(db.String(), nullable=False)
  address = db.Column(db.String())
  phone = db.Column(db.String())
  genres = db.Column(db.ARRAY(db.String(50)), nullable=False)
  image_link = db.Column(db.String())
  facebook_link = db.Column(db.String())
  website = db.Column(db.String())
  seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
  seeking_description = db.Column(db.String())


class Artist(db.Model):
  __tablename__ = "Artist"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  city = db.Column(db.String(), nullable=False)
  state = db.Column(db.String(), nullable=False)
  phone = db.Column(db.String())
  genres = db.Column(db.ARRAY(db.String(50)), nullable=False)
  image_link = db.Column(db.String())
  facebook_link = db.Column(db.String())
  website = db.Column(db.String())
  seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
  seeking_description = db.Column(db.String())


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  data1 = db.session.query(Venue.city,Venue.state).distinct()
  data=[]
  for d in data1:
    venues = Venue.query.filter_by(city=d.city,state=d.state).order_by('id').all()
    datax={
      "city": d.city,
      "state": d.state,
      "venues": []
    }
    for v in venues:
      datax["venues"].append(v)
    data.append(datax)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = request.form.get('search_term', '')
  ven_search = Venue.query.filter(func.lower(Venue.name).contains(func.lower(data)))
  response={
    "count": ven_search.count(),
    "data": ven_search
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1 = Venue.query.filter_by(id=venue_id).first()
  data={
    "id": data1.id,
    "name": data1.name,
    "genres": data1.genres,
    "address": data1.address,
    "city": data1.city,
    "state": data1.state,
    "phone": data1.phone,
    "website": data1.website,
    "facebook_link": data1.facebook_link,
    "seeking_talent": data1.seeking_talent,
    "seeking_description": data1.seeking_description,
    "image_link": data1.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0
  }
  x=Shows.query.join(Venue.shows).filter(Venue.id==venue_id)
  if x.first() != None:
    for a in x:
      datax={
        "artist_id": a.artists[0].id,
        "artist_name": a.artists[0].name,
        "artist_image_link": a.artists[0].image_link,
        "start_time": str(a.start_time)
      }
      if pytz.UTC.localize(datetime.now()) < a.start_time.replace(tzinfo=pytz.UTC) :
        data["upcoming_shows"].append(datax)
      else:
        data["past_shows"].append(datax)
    data["past_shows_count"] = len(data["past_shows"])
    data["upcoming_shows_count"] = len(data["upcoming_shows"])
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    venue = Venue(name = request.form['name'],
                  city = request.form['city'],
                  state = request.form['state'],
                  address = request.form['address'],
                  phone = request.form['phone'],
                  genres = request.form.getlist('genres'),
                  facebook_link = request.form['facebook_link'],
                  seeking_description = request.form['seeking_description'],
                  image_link = request.form['image_link'],
                  website = request.form['website']
                  )
    if request.form['seeking_talent']=='true':
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False

    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  vname = Venue.query.filter_by(id=venue_id).first().name
  try:
    shws = Shows.query.join(Venue.shows).filter(Venue.id==venue_id).all()
    if len(shws)>0:
      for x in shws:
        db.session.delete(x)
    ven = Venue.query.get(venue_id)
    db.session.delete(ven)
    db.session.commit()
    flash('Venue ' + vname + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + vname + ' could not be deleted.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.order_by('name').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = request.form.get('search_term', '')
  art_search = Artist.query.filter(func.lower(Artist.name).contains(func.lower(data)))
  response={
    "count": art_search.count(),
    "data": art_search
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1 = Artist.query.filter_by(id=artist_id).first()
  data={
    "id": data1.id,
    "name": data1.name,
    "genres": data1.genres,
    "city": data1.city,
    "state": data1.state,
    "phone": data1.phone,
    "website": data1.website,
    "facebook_link": data1.facebook_link,
    "seeking_venue": data1.seeking_venue,
    "seeking_description": data1.seeking_description,
    "image_link": data1.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0
  }
  x=Shows.query.join(Artist.shows).filter(Artist.id==artist_id)
  if x.first() != None:
    for a in x:
      datax={
        "venue_id": a.venues[0].id,
        "venue_name": a.venues[0].name,
        "venue_image_link": a.venues[0].image_link,
        "start_time": str(a.start_time)
      }
      if pytz.UTC.localize(datetime.now()) < a.start_time.replace(tzinfo=pytz.UTC) :
        data["upcoming_shows"].append(datax)
      else:
        data["past_shows"].append(datax)
    data["past_shows_count"] = len(data["past_shows"])
    data["upcoming_shows_count"] = len(data["upcoming_shows"])
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.filter_by(id=artist_id).first()
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_descriptio = request.form['seeking_description']
    artist.image_link = request.form['image_link']
    artist.website = request.form['website']
    if request.form['seeking_venue']=='true':
      artist.seeking_venue = True
    else:
      artist.seeking_venue = False

    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.address = request.form['address']
    venue.seeking_description = request.form['seeking_description']
    venue.image_link = request.form['image_link']
    venue.website = request.form['website']
    if request.form['seeking_talent']=='true':
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False

    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    artist = Artist(name = request.form['name'],
                  city = request.form['city'],
                  state = request.form['state'],
                  phone = request.form['phone'],
                  genres = request.form.getlist('genres'),
                  facebook_link = request.form['facebook_link'],
                  seeking_description = request.form['seeking_description'],
                  image_link = request.form['image_link'],
                  website = request.form['website']
                  )
    if request.form['seeking_venue']=='true':
      artist.seeking_venue = True
    else:
      artist.seeking_venue = False
    
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Shows.query.order_by('id').all()
  data=[]
  for d in shows:
    venue = Venue.query.filter_by(id=d.venues[0].id).first()
    artist = Artist.query.filter_by(id=d.artists[0].id).first()
    datax={
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "venue_id": venue.id,
      "venue_name": venue.name,
      "start_time": d.start_time
    }
    data.append(datax)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  artists = Artist.query.order_by('name').all()
  venues = Venue.query.order_by('name').all()
  return render_template('forms/new_show.html', form=form,artists=artists,venues=venues)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    v_id = int(request.form.get('venue_id',''))
    a_id = int(request.form.get('artist_id',''))
    
    sh = Shows(start_time=request.form['start_time'])
    ven = Venue.query.filter_by(id=v_id).first()
    art = Artist.query.filter_by(id=a_id).first()
    sh.artists = [art]
    sh.venues = [ven]
    db.session.commit()
    
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  # on successful db insert, flash success
  
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