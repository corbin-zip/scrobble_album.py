# scrobble_album.py
## Description

scrobble_album.py is a simple Python script designed for scrobbling music tracks via the pylast library. It can also search for albums by an artist by simply providing the artist name. Additionally, you can specify a specific time to scrobble.

## Why?

For scrobbling, I use `yams` with `ncmpcpp` as well as Plex's last.fm integration, but I didn't have a way to scrobble all the vinyl/tapes I listen to. So, I worked with ChatGPT on a simple scrobbler and figured others may find some benefit in it as well!

## API Setup

Create an API key here: https://www.last.fm/api/account/create

Stick the API key in a file `~/.config/pylast/api_key` and the shared secret into `~/.config/pylast/api_secret` -- there should be nothing else in these files, just the key, with no new line

For reference, you can find previous keys/secrets you've created here: https://www.last.fm/api/accounts

## Usage 

`python scrobble_album.py 'Artist Name' [Album Name] [Time]`

## Arguments

1. Artist Name: This argument is mandatory and represents the name of the artist.

2. Album Name: This argument is optional. If you specify it, the script will scrobble the given album by the artist at the current time. If you leave it blank, the script will search for albums by the given artist.

3. Time: This argument is optional. If you specify it, the script will scrobble at the given time in the 'HH:MM AM/PM' format (note that there must be a space between HH:MM and AM or PM). If you leave it blank, the script will scrobble at the current time if an album is specified.

## Example

To scrobble an album at a specific time:

`python scrobble_album.py 'Pink Floyd' 'The Dark Side of the Moon' '08:30 PM'`

To scrobble an album right now:

`python scrobble_album.py 'Pink Floyd' 'The Dark Side of the Moon'`

To search for albums by an artist:

`python scrobble_album.py 'Pink Floyd'`

## Dependencies

### pylast

On Arch Linux with `yay`, I install via `yay pylast`

But the install directions are also available:

* https://pypi.org/project/pylast/
* https://github.com/pylast/pylast