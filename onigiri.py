#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import logging.config
import configparser
import urllib.request
import urllib.parse
import json
import datetime
import time
import threading


CONFIG_FILE = os.path.dirname(os.path.abspath(__file__)) + '/onigiri.config'

TWITCASTING_API_LIVE_STATUS = 'http://api.twitcasting.tv/api/livestatus'
PARSE_API_PUSH = 'https://api.parse.com/1/push'
# LIVE_TOO_CLOSE_THREASHOLD is used for avoiding unnecessary alert that is caused by temporary
# live interruption. (seconds)
LIVE_TOO_CLOSE_THREASHOLD = 60 * 2  # 2 min


class OnigiriAlert(object):
# magic methods
    def __init__(self, user, sound, polling_interval, push_expire_time,
                 parse_application_id, parse_rest_api_key, subchannel=''):
        self.user = user
        self.sound = sound
        self.polling_interval = polling_interval
        self.push_expire_time = push_expire_time
        self.parse_application_id = parse_application_id
        self.parse_rest_api_key = parse_rest_api_key
        self.subchannel = subchannel

# public methods
    def listen(self):
        logging.debug(u'OnigiriAlert.listen() started.')

        url = TWITCASTING_API_LIVE_STATUS + '?type=json&user=' + self.user
        last_is_live = None
        last_live_datetime = datetime.datetime.now() - datetime.timedelta(days=1)

        while True:
            try:
                is_live_started = False

                request = urllib.request.urlopen(url)
                encoding = request.headers.get_content_charset()
                response = request.read().decode(encoding)
                # logging.debug(response)

                parsed = json.loads(response)
                logging.debug(parsed)
                is_live = parsed["islive"]

                if last_is_live is None:
                    pass
                elif last_is_live is False and is_live is True:
                    is_live_started = True

                last_is_live = is_live

                # notification section
                if is_live_started is True:
                    timedelta_since_last_live = datetime.datetime.now() - last_live_datetime
                    live_too_close_threashold = datetime.timedelta(
                        seconds=LIVE_TOO_CLOSE_THREASHOLD)
                    if timedelta_since_last_live < live_too_close_threashold:
                        logging.info("live is too close to previous live, so skip. "
                                     "last_live_datetime: {}".format(last_live_datetime))
                    else:
                        self.notify(parsed)

                if last_is_live is True:
                    last_live_datetime = datetime.datetime.now()

                # raise Exception('test exception')
            except Exception as error:
                logging.error("caught exception in polling loop, error: [{}]".format(error))
                # os.sys.exit()

            time.sleep(self.polling_interval)

        logging.debug(u'OnigiriAlert.listen() ended.')

# private methods
    def notify(self, parsed):
        headers = {'X-Parse-Application-Id': self.parse_application_id,
                   'X-Parse-REST-API-Key': self.parse_rest_api_key,
                   'Content-Type': 'application/json'}

        channel = 'ts{0:02d}'.format(datetime.datetime.now().hour)
        message = "配信「{}{}」がはじまりました.".format(parsed["title"], parsed["subtitle"])
        expire = int(time.time()) + self.push_expire_time

        parameters = {'where': {'channels': channel},
                      'data': {'alert': message, 'sound': self.sound},
                      'expiration_time' : expire}
        if self.subchannel != '':
            parameters['where']['subChannels'] = self.subchannel

        dumped_parameters = json.dumps(parameters).encode('utf-8')
        logging.info(dumped_parameters)

        request = urllib.request.Request(PARSE_API_PUSH, dumped_parameters, headers)
        response = urllib.request.urlopen(request).read()
        logging.info(response)


def main():
    config_file = CONFIG_FILE
    if len(sys.argv) == 2:
        config_file = sys.argv[1]

    logging.config.fileConfig(config_file)

    config = configparser.ConfigParser()
    config.read(config_file)

    section = 'application'
    main_user = config[section]['main_user']
    main_sound = config[section]['main_sound']
    sub_users = config[section]['sub_users'].split(',')
    sub_sounds = config[section]['sub_sounds'].split(',')
    polling_interval = float(config[section]['polling_interval'])
    push_expire_time = int(config[section]['push_expire_time'])

    section = 'parse'
    parse_application_id = config[section]['application_id']
    parse_rest_api_key = config[section]['rest_api_key']

    logging.debug("main_user:{} main_sound:{} sub_users:{} sub_sounds:{} "
            "polling_interval:{} push_expire_time: {} "
                  "parse_application_id:{} parse_rest_api_key:{}"
                  .format(main_user, main_sound, sub_users, sub_sounds,
                          polling_interval, push_expire_time,
                          parse_application_id, parse_rest_api_key))

    logging.info(u'started.')
    threads = []

    # main user
    onigiri = OnigiriAlert(main_user, main_sound, polling_interval, push_expire_time,
                           parse_application_id, parse_rest_api_key)
    thread = threading.Thread(name=main_user, target=onigiri.listen)
    thread.start()
    threads.append(thread)

    # sub users
    sound_index = 0
    for sub_user in sub_users:
        sub_sound = sub_sounds[sound_index]
        onigiri = OnigiriAlert(sub_user, sub_sound, polling_interval, push_expire_time,
                               parse_application_id, parse_rest_api_key, sub_user)
        thread = threading.Thread(name=sub_user, target=onigiri.listen)
        thread.start()
        threads.append(thread)
        sound_index += 1

    for thread in threads:
        thread.join()

    logging.info(u'ended.')


if __name__ == "__main__":
    main()
