#!/usr/bin/env python

import sys
import time
import getopt
import socket

try:
    from dop.client import Client
except ImportError, e:
    print "DOP is needed and may be found here:"
    print "    https://github.com/ahmontero/dop"
    sys.exit(-2)


class DigitalOcean():
    def __init__(self, client_id, api_key):
        self.client_id = client_id
        self.api_key = api_key
        self.client = Client(self.client_id, self.api_key)

        # This list in outdated, fixme
        self.regions = {'ny1': 1, 'ams1': 2, 'sf1': 3, 'ny2': 4}

    def droplet_get(self, name):
        for droplet in self.client.show_active_droplets():
            if droplet.to_json()['name'] == name:
                return droplet.to_json()['id']
        return None

    def droplet_create(self, name, region):
        if self.droplet_status(name) is not None:
            return
        droplet = self.client.create_droplet(name, 66, 308287,
                                        self.regions[region])
        return droplet

    def droplet_destroy(self, name):
        if self.droplet_status(name) is None:
            return 0
        print "Removing droplet %s" % name
        self.client.destroy_droplet(self.droplet_get(name))

    def droplet_list(self):
        droplets = self.client.show_active_droplets()
        for droplet in droplets:
            json = droplet.to_json()
            print json['name'] + " ",
            print json['status'] + " ",
            print json['ip_address']


def usage():
    print "Usage: %s takes the following parameters:" % sys.argv[0]
    print "  --list     Shows all droplets"
    print "  --create   Create a new droplet"
    print "  --delete   Remove a droplet"
    print "  --name     Name for new droplets"
    print "  --location Droplet location for new droplets"
    print "  --id       DigitalOcean ID"
    print "  --key      API key"
    sys.exit(0)

if __name__ == '__main__':
    droplets_create = 0
    droplets_list = 0
    droplets_delete = 0
    do_id = ""
    do_key = ""
    optargs = ['list', 'name=', 'create', 'delete', 'location=',
               'id=', 'key=', 'help']

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ln:cdi:k:p:', optargs)
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt == '-h':
            usage()
        elif opt in ('-l', '--list'):
            droplets_list = 1
        elif opt in ('-n', '--name'):
            droplet_name = arg
        elif opt in ('-c', '--create'):
            droplets_create = 1
        elif opt in ('-d', '--delete'):
            droplets_delete = 1
        elif opt in ('-p', '--location'):
            droplet_location = arg
        elif opt in ('-i', '--id'):
            do_id = arg
        elif opt in ('-k', '--key'):
            do_key = arg
        else:
            usage()

    if not any([droplets_create, droplets_list, droplets_delete]):
        usage()

    if (droplets_create + droplets_list + droplets_delete) > 1:
        usage()

    if do_id is "" or do_key is "":
        usage()

    try:
        do = DigitalOcean(do_id, do_key)
        if droplets_list:
            do.droplet_list()
        if droplets_create:
            do.droplet_create(droplet_name, droplet_location)
        if droplets_delete:
            do.droplet_destroy(droplet_name)
    except Exception, e:
        print 'Failed with error: %s' % e
