#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Service for listening and handling Queue Messages.

This service registers interest in listening to a Queue and processing received messages.
"""
import asyncio
import functools
import getopt
import json
import os
import random
import signal
import sys

from entity_queue_common.service_utils import error_cb, logger, signal_handler
from nats.aio.client import Client as NATS  # noqa N814; by convention the name is NATS
from stan.aio.client import Client as STAN  # noqa N814; by convention the name is STAN


async def run(loop, old_identifier, new_identifier):  # pylint: disable=too-many-locals
    """Run the main application loop for the service.

    This runs the main top level service functions for working with the Queue.
    """
    # NATS client connections
    nc = NATS()
    sc = STAN()

    async def close():
        """Close the stream and nats connections."""
        await sc.close()
        await nc.close()

    # Connection and Queue configuration.
    def nats_connection_options():
        return {
            'servers': os.getenv('NATS_SERVERS', 'nats://127.0.0.1:4222').split(','),
            'io_loop': loop,
            'error_cb': error_cb,
            'name': os.getenv('NATS_ENTITY_EVENTS_CLIENT_NAME', 'entity.events.worker')
        }

    def stan_connection_options():
        return {
            'cluster_id': os.getenv('NATS_CLUSTER_ID', 'test-cluster'),
            'client_id': str(random.SystemRandom().getrandbits(0x58)),
            'nats': nc
        }

    def subscription_options():
        return {
            'subject': os.getenv('NATS_ENTITY_EVENTS_SUBJECT', 'entity.events'),
            'queue': os.getenv('NATS_ENTITY_EVENTS_QUEUE', 'events-worker'),
            'durable_name': os.getenv('NATS_ENTITY_EVENTS_QUEUE', 'events-worker') + '_durable'
        }

    try:
        # Connect to the NATS server, and then use that for the streaming connection.
        await nc.connect(**nats_connection_options())
        await sc.connect(**stan_connection_options())

        # register the signal handler
        for sig in ('SIGINT', 'SIGTERM'):
            loop.add_signal_handler(getattr(signal, sig),
                                    functools.partial(signal_handler, sig_loop=loop, sig_nc=nc, task=close)
                                    )

        payload = {
            'specversion': '1.x-wip',
            'type': 'bc.registry.business.incorporationApplication',
            'source': 'https://api.business.bcregistry.gov.bc.ca/v1/business/BC1234567/filing/12345678',
            'id': 'C234-1234-1234',
            'time': '2020-08-28T17:37:34.651294+00:00',
            'datacontenttype': 'application/json',
            'identifier': new_identifier,
            'tempidentifier': old_identifier,
            'data': {
                'filing': {
                    'header': {'filingId': '12345678'},
                    'business': {'identifier': 'BC1234567'}
                }
            }
        }

        print('payload-->', payload)

        await sc.publish(subject=subscription_options().get('subject'),
                         payload=json.dumps(payload).encode('utf-8'))

    except Exception as e:  # pylint: disable=broad-except
        # TODO tighten this error and decide when to bail on the infinite reconnect
        logger.error(e)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:n:", ["oldid=", "newid="])
    except getopt.GetoptError:
        print('q_cli.py -o <old_identifier> -n <new_identifier>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('q_cli.py -o <old_identifier> -n <new_identifier>')
            sys.exit()
        elif opt in ("-o", "--oldid"):
            old_id = arg
        elif opt in ("-n", "--newid"):
            new_id = arg

    print('publish:', old_id, new_id)
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(run(event_loop, old_id, new_id))
