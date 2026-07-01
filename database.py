from tinydb import TinyDB, Query

db = TinyDB("db.json")

songs = db.table("songs")
users = db.table("users")


def add_song(song):
    songs.insert(song)


def all_songs():
    return songs.all()


def next_code():
    return len(songs.all()) + 1


def find_by_code(code):
    Q = Query()
    res = songs.search(Q.code == code)
    return res[0] if res else None


def search_by_name(text):
    Q = Query()
    return songs.search(Q.name.test(lambda x: text.lower() in x.lower()))


def add_user(uid):
    Q = Query()
    if not users.search(Q.id == uid):
        users.insert({"id": uid})


def users_count():
    return len(users.all())


def songs_count():
    return len(songs.all())
