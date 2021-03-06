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


CONFIG_FILE = os.path.dirname(os.path.abspath(__file__)) + '/onigiri.config'

TWITCASTING_API_LIVE_STATUS = 'http://api.twitcasting.tv/api/livestatus'
PARSE_API_PUSH = 'https://api.parse.com/1/push'
POLLING_INTERVAL = 1.2
PUSH_EXPIRE_TIME = 60 * 10  # 10 min
# LIVE_TOO_CLOSE_THREASHOLD is used for avoiding unnecessary alert that is caused by temporary
# live interruption. (seconds)
LIVE_TOO_CLOSE_THREASHOLD = 60 * 2  # 2 min


class OnigiriAlert(object):
# magic methods
    def __init__(self, user, parse_application_id, parse_rest_api_key):
        self.user = user
        self.parse_application_id = parse_application_id
        self.parse_rest_api_key = parse_rest_api_key

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

            time.sleep(POLLING_INTERVAL)

        logging.debug(u'OnigiriAlert.listen() ended.')

# private methods
    def notify(self, parsed):
        headers = {'X-Parse-Application-Id': self.parse_application_id,
                   'X-Parse-REST-API-Key': self.parse_rest_api_key,
                   'Content-Type': 'application/json'}

        channel = 'ts{0:02d}'.format(datetime.datetime.now().hour)
        message = "配信「{}{}」がはじまりました.".format(parsed["title"], parsed["subtitle"])
        expire = int(time.time()) + PUSH_EXPIRE_TIME

        parameters = {'channels': [channel],
                      'data': {'alert': message, 'sound': 'horagai.aiff'},
                      'expiration_time' : expire}
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
    user = config[section]['user']

    section = 'parse'
    parse_application_id = config[section]['application_id']
    parse_rest_api_key = config[section]['rest_api_key']

    logging.debug("user:{} parse_application_id:{} parse_rest_api_key:{}".format(
        user, parse_application_id, parse_rest_api_key))

    logging.info(u'started.')
    onigiri = OnigiriAlert(user, parse_application_id, parse_rest_api_key)
    onigiri.listen()
    logging.info(u'ended.')


if __name__ == "__main__":
    main()
