#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  data = []
  venues_query = Venue.query.distinct(Venue.city,Venue.state).all()
  for venue in  venues_query:
        filter_venues = Venue.query.filter_by(city=venue.city,state=venue.state).all()
        upcoming_shows = len(Show.query.filter(venue.id == Show.venue_id).all())
        venue_data = []
        for v in filter_venues:
            venue_data.append({
               "id": v.id,
               "name": v.name,
               "num_upcoming_shows": upcoming_shows 
               })  
        data.append({"city": venue.city,"state": venue.state,"venues": venue_data})

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  try:
    result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    count = len(result)
    response = {
        'count' : count,
        'data'  : result
      }
  except:
    return 'Error occured while fetching results'
  finally:
     return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
 
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  venue = Venue.query.filter(Venue.id == venue_id).first()
  past = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  upcoming = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  past_list = []
  upcoming_list = []
  total_past_shows = len(past)
  total_upcoming_shows = len(upcoming)

  for show in past:
     past_list.append(
        {
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
        }
     )
  for show in upcoming:
     upcoming_list.append(
        {
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
        }
     )
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": json.loads(venue.genres),
    "address":venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_list,
    "upcoming_shows": upcoming_list,
    "past_shows_count": total_past_shows,
    "upcoming_shows_count": total_upcoming_shows,
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  
  if(request.form.get('seeking_talent') == 'y'):
     seeking_talent = True
  else:
     seeking_talent = False
  try:
     venue = Venue(
         name  = request.form.get('name'),
         city = request.form.get('city'),
         state = request.form.get('state'),
         address = request.form.get('address'),
         phone = request.form.get('phone'),
         genres = json.dumps(request.form.getlist('genres')),
         facebook_link = request.form.get('facebook_link'),
         image_link = request.form.get('image_link'),
         website = request.form.get('website'),
         seeking_talent = seeking_talent,
         seeking_description = request.form.get('seeking_description')
       )
     db.session.add(venue)
     db.session.commit()
     flash('Venue ' + venue.name + ' was successfully listed!')
     return redirect(url_for('show_venue',venue_id = venue.id))     
  except:
     db.session.rollback()
     flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
     db.session.close()
     return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  venue = Venue.query.get_or_404(venue_id)
  try:
     db.session.delete(venue)
     db.session.commit()
  except:
     db.session.fallback()
  finally:
     db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  count = len(result)
  response = {
    'count': count,
    'data': result
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter(Artist.id == artist_id).first()
  past = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
  upcoming = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  past_list = []
  upcoming_list = []
  total_past_shows = len(past)
  total_upcoming_shows = len(upcoming)

  for show in past:
     past_list.append(
        {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
        }
     )
  for show in upcoming:
     upcoming_list.append(
        {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
        }
     )
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": json.loads(artist.genres),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_list,
    "upcoming_shows": upcoming_list,
    "past_shows_count": total_past_shows,
    "upcoming_shows_count": total_upcoming_shows,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm(request.form)
  
  artist = Artist.query.filter(Artist.id == artist_id).first()
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = json.loads(artist.genres)
  form.website_link.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": json.loads(artist.genres),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  if(request.form.get('seeking_venue') == 'y'):
     seeking_venue = True
  else:
     seeking_venue = False
  artist = Artist.query.get_or_404(artist_id)
  artist.name = request.form.get('name')
  artist.city = request.form.get('city')
  artist.state = request.form.get('state')
  artist.phone = request.form.get('phone')
  artist.genres = json.dumps(request.form.getlist('genres'))
  artist.facebook_link = request.form.get('facebook_link')
  artist.image_link = request.form.get('image_link')
  artist.website = request.form.get('website_link')
  artist.seeking_venue = seeking_venue
  artist.seeking_description = request.form.get('seeking_description')  
  
  try:
     db.session.add(artist)
     db.session.commit()
     flash('Artist ' + artist.name + ' was successfully updated!')
  except:
     db.session.rollback()
     flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  finally:
     db.session.close()
     return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id).first()
  form.name.data = venue.name
  form.genres.data = json.loads(venue.genres)
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link

  venue={
    "id": venue.id,
    "name": venue.name,
    "genres": json.loads(venue.genres),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  if(request.form.get('seeking_talent') == 'y'):
     seeking_talent = True
  else:
     seeking_talent = False
  venue = Venue.query.get_or_404(venue_id)
  venue.name = request.form.get('name')
  venue.city = request.form.get('city')
  venue.state = request.form.get('state')
  venue.address = request.form.get('address')
  venue.phone = request.form.get('phone')
  venue.genres = json.dumps(request.form.getlist('genres'))
  venue.facebook_link = request.form.get('facebook_link')
  venue.image_link = request.form.get('image_link')
  venue.website = request.form.get('website_link')
  venue.seeking_talent = seeking_talent
  venue.seeking_description = request.form.get('seeking_description')    
  try:
     form.populate_obj(venue)
     db.session.add(venue)
     db.session.commit()
     flash('Venue ' + venue.name + ' was successfully updated!')
  except:
     db.session.rollback()
     flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
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
  # TODO: Validation Pending
  form = ArtistForm(request.form)  
  if(request.form.get('seeking_venue') == 'y'):
     seeking_venue = True
  else:
     seeking_venue = False  
  artist = Artist(
    name = request.form.get('name'),
    city = request.form.get('city'),
    state = request.form.get('state'),
    phone = request.form.get('phone'),
    genres = json.dumps(request.form.getlist('genres')),
    facebook_link = request.form.get('facebook_link'),
    image_link = request.form.get('image_link'),
    website = request.form.get('website_link'),
    seeking_venue = seeking_venue,  
    seeking_description = request.form.get('seeking_description')
  )
  try:
     db.session.add(artist)
     db.session.commit()
     flash('Artist ' + artist.name + ' was successfully listed!')
  except:
     db.session.rollback()
     flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  finally:
     db.session.close()
     return render_template('pages/home.html')
  
  
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows_query = db.session.query(Venue.id,Venue.name,Artist.id,Artist.name,Artist.image_link,Show.start_time).filter(Artist.id==Show.artist_id,Venue.id == Show.venue_id).all()
  data = []
  print(shows_query)
  for show in shows_query:   
    data.append({
      "venue_id": show[0],
      "venue_name": show[1],
      "artist_id": show[2],
      "artist_name": show[3],
      "artist_image_link": show[4],
      "start_time": str(show[5])
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  show = Show(
              artist_id  = request.form.get('artist_id'),
              venue_id   = request.form.get('venue_id'),
              start_time = request.form.get('start_time')
          )
  try:
     db.session.add(show)
     db.session.commit()
     flash('Show was successfully listed!')
     print('Listed')
  except:
     db.session.rollback()
     flash('An error occurred. Show could not be listed.')
     print('Error')
  finally:
     db.session.close()
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
