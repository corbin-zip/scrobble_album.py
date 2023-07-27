import datetime
import sys
import pylast
import os
import time

# Define the paths to the files
CONFIG_DIR = os.path.expanduser("~/.config/pylast/")
API_KEY_FILE = os.path.join(CONFIG_DIR, "api_key")
API_SECRET_FILE = os.path.join(CONFIG_DIR, "api_secret")
SESSION_KEY_FILE = os.path.join(CONFIG_DIR, ".session_key")

# Dry run, yes or no?
DRY = False

# Make sure the API_KEY and API_SECRET files exist
if not os.path.exists(API_KEY_FILE) or not os.path.exists(API_SECRET_FILE):
    print("API_KEY and/or API_SECRET file(s) not found.")
    sys.exit(1)

# Read API_KEY and API_SECRET from their files
with open(API_KEY_FILE, 'r') as file:
    API_KEY = file.read().strip()

with open(API_SECRET_FILE, 'r') as file:
    API_SECRET = file.read().strip()

# Check if the session key file exists, if not generate and save session key
if not os.path.exists(SESSION_KEY_FILE):
    skg = pylast.SessionKeyGenerator(network)
    url = skg.get_web_auth_url()

    print(f"Please authorize this script to access your account: {url}\n")
    import webbrowser
    webbrowser.open(url)

    while True:
        try:
            SESSION_KEY = skg.get_web_auth_session_key(url)
            with open(SESSION_KEY_FILE, "w") as f:
                f.write(SESSION_KEY)
            break
        except pylast.WSError:
            time.sleep(1)
else:
    with open(SESSION_KEY_FILE, 'r') as file:
        SESSION_KEY = file.read().strip()

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, session_key=SESSION_KEY)

def search_albums(artist):
    artist_obj = network.get_artist(artist)
    albums = artist_obj.get_top_albums(limit=10)
    n_albums = len(albums)

    # print albums in reverse order (most popular at the bottom)
    for index, album in enumerate(reversed(albums), 1):
        try:
            track_count = len(album.item.get_tracks())
            album_name = album.item.get_name()
            print(f'#{n_albums-index+1}: {album_name} ({track_count} tracks)')

        except pylast.WSError as e:
            print(f"#{n_albums - index + 1}: error while processing album: {e}")
            continue  # Skip to the next album
    
    print("#0: to do nothing & exit")
    while True:
        try:
            user_input = int(input("scrobble #> "))
            if user_input == 0:
                print("BYE BYE")
                break
            elif 1 <= user_input <= (n_albums + 1):
                # TODO: write the time in the print statement on line 81
                # TODO: maybe do (enter for [time]) and it displays the current time
                time_input = str(input("time? (push enter for current time) > "))
                if (time_input == ''):
                    time_input = None
                album_selected_name = albums[user_input - 1].item.get_name()
                print(f'attempting to scrobble "{album_selected_name}...')
                scrobble_album(artist, album_selected_name, time_input)
                break
            else:
                print("scrobble #> ")
        except ValueError:
            print("error: you either selected an album that is out of bounds, " \
                    "or you did not follow the correct time format (HH:MM AM)")



def scrobble_album(artist, album, time_str=None):
    album_info = network.get_album(artist, album)

    tracks = album_info.get_tracks()

    # TODO: should allow user to write something like 5:55pm/PM etc, uppercase/lowercase
    #       with/without the space
    now = int(time.time())
    if time_str is not None:
        # Convert the input time string to a time object
        time_obj = datetime.datetime.strptime(time_str, "%I:%M %p").time()
        # Get the current date and combine with the input time to form a datetime object
        today_date = datetime.date.today()
        now = int(datetime.datetime.combine(today_date, time_obj).timestamp())

    # Calculate the scrobble times for each track
    scrobble_times = []
    total_duration = sum(track.get_duration() for track in tracks)
    #print(tracks)
    try:
        album_title = tracks[0].get_album().title
    except AttributeError:
        # trouble grabbing album title from first track; defaulting to whatever user input was
        album_title = album
    except IndexError:
        # TODO: maybe just hide 0 track albums then? this error will
        # still be needed for manual 'Artist' 'Album' scrobbles though
        print("sorry! last.fm doesn't think that album has any tracks, so it can't be scrobbled")
        exit()

    for track in reversed(tracks):
        track_duration = track.get_duration()
        total_duration -= track_duration

        # Calculate the timestamp for this track's scrobble time
        timestamp = now - (total_duration) // 1000
        # Add the scrobble time to the list
        scrobble_times.append(timestamp)

    # Scrobble each track at the corresponding scrobble time
    for i, track in enumerate(tracks):
        le_time = time.strftime("%I:%M %p", time.localtime(scrobble_times[i]))
        print(f"Track {i+1} - {track.title} @ {le_time}")
        if (not DRY):
            network.scrobble(
                artist=track.artist.name,
                title=track.title,
                album=album_title,
                timestamp=scrobble_times[i]
            )


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Usage: python scrobble_album.py 'Artist Name' [Album Name] [Time]")
        sys.exit(1)

    artist_name = sys.argv[1]

    # Check if album name is supplied
    if len(sys.argv) > 2:
        album_name = sys.argv[2]
    else:
        album_name = None

    # Check if time_str is supplied
    if len(sys.argv) == 4:
        time_str = sys.argv[3]
    else:
        time_str = None

    # If album name is not provided, search albums instead of scrobbling
    if album_name is None:
        search_albums(artist_name)
    else:
        scrobble_album(artist_name, album_name, time_str)
