from tinydb import TinyDB, Query


db = TinyDB("db.json")


songs = db.table("songs")
users = db.table("users")



def add_song(song):

    songs.insert(song)



def get_songs():

    return songs.all()



def find_song(song_id):

    Song = Query()

    result = songs.search(
        Song.id == song_id
    )

    if result:
        return result[0]

    return None



def add_user(user_id):

    User = Query()

    exists = users.search(
        User.id == user_id
    )

    if not exists:

        users.insert({
            "id": user_id
        })



def user_count():

    return len(users.all())



def song_count():

    return len(songs.all())
