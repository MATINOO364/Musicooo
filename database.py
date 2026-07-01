from tinydb import TinyDB, Query


db = TinyDB("db.json")


songs = db.table("songs")
users = db.table("users")



def add_song(data):

    songs.insert(data)



def all_songs():

    return songs.all()



def get_next_id():

    if not songs.all():
        return 1

    return len(songs.all()) + 1



def find_song(code):

    Q = Query()

    result = songs.search(
        Q.code == int(code)
    )

    if result:
        return result[0]

    return None



def search_name(name):

    Q = Query()

    result = songs.search(
        Q.name.test(
            lambda x: name.lower() in x.lower()
        )
    )

    return result



def add_user(uid):

    Q = Query()

    if not users.search(Q.id == uid):

        users.insert({
            "id":uid
        })



def users_count():

    return len(users.all())



def songs_count():

    return len(songs.all())
