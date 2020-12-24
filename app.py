import os
import redis
import flask
import random

app = flask.Flask(__name__)
redis_conn = redis.from_url(os.environ['REDIS_URL'], decode_responses=True)

instructions = [
    """\
<ol>
<li> <b>Round 1</b>
<li> No passing
<li> Say anything, hum, gesture
<li> No words in the name or rhyming clues
<li> Any number of guesses
</ol>
""", """\
<ol>
<li> <b> Round 2</b>
<li> Passing allowed, cannot revisit names
<li> Say a single word, hum, gesture
<li> One guess allowed
</ol>
""", """\
<ol>
<li> <b> Round 3</b>
<li> Passing allowed, cannot revisit names
<li> No words; only humming, sound effects, gestures
<li> One guess allowed
</ol>
""", """\
<ol>
<li> <b>Game Over</b>
</ol>
"""
 ]

class Room:
  def __init__(self, room_id):
    self.id = room_id
    if redis_conn.get(f"{self.id}:round") is None:
      redis_conn.set(f"{self.id}:round", "1")

  @property
  def names_left(self):
    return redis_conn.smembers(f"{self.id}:names_left")

  @property
  def names_guessed(self):
    return redis_conn.smembers(f"{self.id}:names_guessed")

  def add_name(self, name):
    redis_conn.sadd(f"{self.id}:names_left", name)

  def guess_name(self, name):
    redis_conn.smove(f"{self.id}:names_left",
                     f"{self.id}:names_guessed",
                     name)

  @property
  def round(self):
    return int(redis_conn.get(f"{self.id}:round"))

  def next_round(self):
    redis_conn.incr(f"{self.id}:round")

  def reset(self):
    redis_conn.sunionstore(f"{self.id}:names_left",
                           f"{self.id}:names_left",
                           f"{self.id}:names_guessed")
    redis_conn.sdiffstore(f"{self.id}:names_guessed",
                          f"{self.id}:names_guessed",
                          f"{self.id}:names_left")

  def restart(self):
    redis_conn.delete(f"{self.id}:names_guessed", f"{self.id}:names_left")
    redis_conn.set(f"{self.id}:round", "1")

@app.route('/<room_id>', methods=['GET'])
def main(room_id):
  room = Room(room_id)
  return flask.render_template('main.html', room=room, instructions=instructions[room.round-1])
    
@app.route('/<room_id>/names', methods=['GET', 'POST'])
def names(room_id):
  room = Room(room_id)
  if flask.request.method == 'GET':
    return flask.render_template('names.html', room=room)
  else:
    form_names = flask.request.form['names'].split('\r\n')
    for name in form_names:
      name = name.strip()
      if name: room.add_name(name)
    return flask.redirect(flask.url_for('main', room_id=room_id))

@app.route('/<room_id>/play', methods=['GET', 'POST'])
def play(room_id):
  room = Room(room_id)
  if flask.request.method == 'GET':
    names_left = list(room.names_left)
    random.shuffle(names_left)
    return flask.render_template('play.html', names_left=names_left, room=room)
  else:
    for name in flask.request.json:
      room.guess_name(name)

    if not room.names_left:
      room.reset()
      room.next_round()

    return '', 200

@app.route('/<room_id>/newgame')
def newgame(room_id):
  room = Room(room_id)
  room.restart()
  return flask.redirect(flask.url_for('main', room_id=room_id))

if __name__ == '__main__':
  app.run()
