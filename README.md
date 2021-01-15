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
    * Songs (TBA)

Input can be given in the form of a delimited list of strings such as `|` or `,`

## Example Usage

First, you need to authenticate yourself before proceeding.
That can be done by doing the following:

```bash
./funnel --authenticate
```

After authentication, you can use the following actions:

### Merging

```bash
# From a string (not as neat)

funnel --merge --from-list 'https://open.spotify.com/playlist/37i9dQZF1DXasneILDRM7B|https://open.spotify.com/playlist/0GMRiKLyYuKUg3BXyFKNqT' --delimiter '|' --output "Punk Fun"
```

```bash
# From a file (more compact)

funnel --merge --from-file 'punk_playlist_compilation' --output "Punk Fun"
```

### Cloning

```bash
# Small batch

funnel --clone "https://open.spotify.com/playlist/37i9dQZF1DXasneILDRM7B"
```

```bash
# Large batch (clunky)

funnel --batch-clone --from-list 'https://open.spotify.com/playlist/37i9dQZF1DXasneILDRM7B|https://open.spotify.com/playlist/0GMRiKLyYuKUg3BXyFKNqT' --delimiter '|'
```

```bash
# Large batch (preferred)

funnel --batch-clone --from-file 'punk_playlist_compilation'

# Each are created rather a catenation in the --merge option
```

```bash
# Clone an entire user's *public* playlist library
# TBA

funnel --batch-clone --from-user '[LINK(S) TO PROFILE]' --delimiter '|' 
# Description: Cloned playlist from {username} at {current time} (apart of user dump)
# Mostly used for migration purposes from account to account
# add --allow-private-playlists ?

```
