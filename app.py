import os
import redis
import flask
import random

app = flask.Flask(__name__)
redis_conn = redis.from_url(os.environ['REDIS_URL'], decode_responses=True)

class Room:
  def __init__(self, room_id):
    self.room_id = room_id

  @property
  def names_left(self):
    return redis_conn.smembers(f"{self.room_id}:names_left")

  @property
  def names_guessed(self):
    return redis_conn.smembers(f"{self.room_id}:names_guessed")

  def add_name(self, name):
    redis_conn.sadd(f"{self.room_id}:names_left", name)

  def guess_name(self, name):
    redis_conn.smove(f"{self.room_id}:names_left",
                     f"{self.room_id}:names_guessed",
                     name)

  def reset(self):
    redis_conn.sunionstore(f"{self.room_id}:names_left",
                           f"{self.room_id}:names_left",
                           f"{self.room_id}:names_guessed")
    redis_conn.sdiffstore(f"{self.room_id}:names_guessed",
                          f"{self.room_id}:names_guessed",
                          f"{self.room_id}:names_left")

@app.route('/<room_id>/names', methods=['GET', 'POST'])
def names(room_id):
  if flask.request.method == 'GET':
    return flask.render_template('main.html', room_id=room_id)
  else:
    room = Room(room_id)
    form_names = flask.request.form['names'].split('\r\n')
    for name in form_names:
      name = name.strip()
      if name: room.add_name(name)
    return flask.redirect('play')

@app.route('/<room_id>/lobby', methods=['GET'])
def lobby(room_id):
    return flask.render_template('lobby.html', room_id=room_id)

@app.route('/<room_id>/play', methods=['GET', 'POST'])
def play(room_id):
  room = Room(room_id)
  if flask.request.method == 'GET':
    names_left = list(room.names_left)
    random.shuffle(names_left)
    return flask.render_template('game.html', room_id = room_id, names_left=names_left)
  else:
    for name in flask.request.json:
      room.guess_name(name)

    if not room.names_left:
      room.reset()
      
    return '', 200

if __name__ == '__main__':
  app.run()
