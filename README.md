# Funnel Cake

This is a fully fledged program that can interact with the Spotify API.
It has these major features:

- Merging playlists
- Cloning playlists
- Removing tracks based on these criteria
    * Explicit
    * Non explicit
    * Live
- Randomly generate playlists based on these criteria
    * Artists
    * Genre

Input can be given in the form of a delimited list of strings such as `|` or `,`

## Getting Started

Please consult the [wiki before proceeding](https://github.com/JaredDyreson/Funnel-Cake/wiki/Getting-Started).

### Merging

```bash
# From a string (not as neat)

python ./funnel.py --merge --from-list 'https://open.spotify.com/playlist/37i9dQZF1DXasneILDRM7B|https://open.spotify.com/playlist/0GMRiKLyYuKUg3BXyFKNqT' --delimiter '|' --output "Punk Fun"
```

```bash
# From a file (more compact)

python ./funnel.py --merge --from-file 'punk_playlist_compilation' --output "Punk Fun"
```

### Cloning

```bash
# Small batch

python ./funnel.py --clone "https://open.spotify.com/playlist/37i9dQZF1DXasneILDRM7B"
```

```bash
# Large batch (clunky)

python ./funnel.py --batch-clone --from-list 'https://open.spotify.com/playlist/37i9dQZF1DXasneILDRM7B|https://open.spotify.com/playlist/0GMRiKLyYuKUg3BXyFKNqT' --delimiter '|'
```

```bash
# Large batch (preferred)

python ./funnel.py --batch-clone --from-file 'punk_playlist_compilation'

# Each are created rather a catenation in the --merge option
```

```bash
# Clone an entire user's *public* playlist library

python ./funnel.py --batch-clone --from-user '[LINK(S) TO PROFILE]' --delimiter '|' 

# Description: Cloned playlist from {username} at {current time} (apart of user dump)
# Mostly used for migration purposes from account to account
```

### Random Playlist

We can randomly generate playlists based on two criteria; artists and genres.
The default number of tracks is 10 however the maximum is 100.
If no criteria is given, the program will use the genres available via the Spotify API and will use at most two genres.
The API actually supports a mixing of artists and genres, allowing for a total of five "dimensions" of complexity.
However, we are only concerned with one avenue of input, however they can support up to five of each.

```bash
python ./funnel.py --random-playlist --from-list "artist:Metallica,Flux Pavillion" --output "Metallic Dubstep"
# if I don't give the amount, the default is 10

# python ./funnel.py --random-playlist --from-list "artist:Metallica,Flux Pavillion" --count 50 --output "Metallic Dubstep"
# Here we have a new playlist of 50 ^
```

```bash
python ./funnel.py --random-playlist --from-list "genre:classical" --output "Classical Trip"
# if I don't give the amount, the default is 10

# python ./funnel.py --random-playlist --from-list "genre:classical" --count 50 --output "Classical Trip"
# Here we have a new playlist of 50 ^
```

```bash
python ./funnel.py --random-playlist
# randomly generates playlist from selected genre (default 10)

# python ./funnel.py --random-playlist --output "Random Playlist Example"
# you can also give it an output name if you feel like it
```
