#! /usr/bin/python -u

import paho.mqtt.client as mqtt
import json
import time
import itertools
import argparse

class Animation(object):

    def __init__(self, name, timeout):
        self._name = name
        self._timeout = timeout

    @property
    def name(self):
        return self._name

    @property
    def timeout(self):
        return self._timeout

ANIMATIONS = []
ANIMATIONS_TIMEOUT = {}

song_json = {
            "file_id": "",
            "song_is_playing": True,
            "speed": "1.0",
            "start_time_millis_since_epoch": 0
            }

def on_message(client, userdata, msg):
    #print(msg.topic + " " + str(msg.payload))
    pass

def send_new_song(client, name):
    new_song = song_json
    new_song['file_id'] = name
    new_song['start_time_millis_since_epoch'] = int(round(time.time() * 1000))
    json_object = json.dumps(new_song)
    client.publish("current-song", json_object)

def iterate_songs(client):
    for item in itertools.cycle(ANIMATIONS):
        print "Now playing {}, Will go to sleep for {} minutes".format(item.name, item.timeout)
        send_new_song(client, item.name)
        time.sleep(item.timeout * 60)

def parse_animations(animations):
    if len(animations) % 2 == 1:
        print 'Animations should be in "animation_name animation_timeout" pairs'
        return False
    for i in range(0, len(animations), 2):
        animation = create_animation(animations[i], animations[i+1])
        if animation is None:
            print "The pair {} {} is not valid".format(animations[i], animations[i+1])
            return False
        else:
            print "Adding animation {} with timeout of {}".format(animation.name, animation.timeout)
            ANIMATIONS.append(animation)

    return True

def create_animation(animation_name, animation_timeout):
    try:
        animation_timeout = float(animation_timeout)
    except Exception:
        print "Animation timeout must be a number!"
        return None

    return Animation(animation_name, animation_timeout)

def run_player(host):
    client = mqtt.Client()
    client.on_message = on_message
    while True:
        try:
            client.connect(host)
            break
        except Exception:
            time.sleep(0.1)
            continue
    client.subscribe("current-song", 2)
    client.loop_start()
    iterate_songs(client)
    client.loop_stop()

def main():
    parser = argparse.ArgumentParser(description="MQTT Player")
    parser.add_argument('--config', default='/etc/fake_player.conf', required=False, type=str, help='The MQTT host to connect to')
    args = parser.parse_args()
    conf = open(args.config, "r+")
    host = conf.readline().strip()
    animations = conf.readline().split()
    if not parse_animations(animations):
        print "Invalid Animations list!"
        return 1
    else:
        print ""
        run_player(host)


    

if __name__ == "__main__":
    main()
