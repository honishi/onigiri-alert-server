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
PUSH_EXPIRE_TIME = 60 * 60  # 1h

# DEBUG_FORCE_PUSH = True
DEBUG_FORCE_PUSH = False


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

        while True:
            try:
                request = urllib.request.urlopen(url)
                encoding = request.headers.get_content_charset()
                response = request.read().decode(encoding)
                # logging.debug(response)

                parsed = json.loads(response)
                logging.debug(parsed)
                is_live = parsed["islive"]

                if last_is_live is None:
                    pass
                elif last_is_live is False and is_live is True or DEBUG_FORCE_PUSH:
                    self.notify(parsed)
                    if DEBUG_FORCE_PUSH:
                        os.sys.exit()

                last_is_live = is_live
                # raise Exception('test exception')
            except Exception as error:
                logging.error("caught exception in polling loop, error: [{}]".format(error))
                # os.sys.exit()

            time.sleep(POLLING_INTERVAL)

        logging.debug(u'OnigiriAlert.listen() ended.')

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
