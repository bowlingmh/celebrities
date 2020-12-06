import os
import redis
import flask

app = flask.Flask(__name__)
redis_conn = redis.from_url(os.environ['REDIS_URL'])

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


    
    

