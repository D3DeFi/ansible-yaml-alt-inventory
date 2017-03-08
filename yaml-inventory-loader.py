#!/usr/bin/env python

import os
import sys
import yaml
import argparse
try:
    import json
except:
    import simplejson as json

from ansible.inventory import expand_hosts as expand


def scan_inv_directory():
    """Function scans inventory directory for all files ending with .yml
    and tries to parse them into Python dict object."""
    invhosts = {}
    invfiles = os.listdir('inventory')

    # Scan every yml file found inside inventory directory
    for invfile in [x for x in invfiles if x.endswith('.yml')]:
        with open('inventory/{}'.format(invfile), 'r') as inventory:
            try:
                hosts = yaml.safe_load(inventory)
            except yaml.scanner.ScannerError as e:
                print('Inventory syntax error {}'.format(str(e.context_mark).lstrip()))
                sys.exit(1)

        # If there are hosts defined with range indicator [1:3], expand them
        hosts_expanded = {}
        for key, val in hosts.iteritems():
            if expand.detect_range(key):
                key = expand.expand_hostname_range(key)
                hosts_expanded.update({x:val for x in key})
            else:
                hosts_expanded[key] = val

        invhosts.update(hosts_expanded)

    if not invhosts:
        print('No hosts found.')
        sys.exit(1)
    return invhosts


def produce_json_object_list(invhosts):
    """Function parses Python dictionary object representing YAML data
    and produces valid JSON object for Ansible."""
    inventory = {}
    for key, val in invhosts.iteritems():
        groups = val.get('groups', None).replace(' ', '').split(',')
        for group in groups:
            if group in inventory.keys():
                inventory[group].append(key)
            else:
                inventory[group] = [key]

    return json.dumps(inventory, indent=2)


def produce_json_object_host(invhosts, host):
    """Function parses Python dictionary object representing YAML data
    and produces valid JSON object for Ansible."""
    host_vars = invhosts.get(host, {})
    return json.dumps(host_vars, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Alternative YAML dynamic inventory')
    parser.add_argument('--list', default=False, dest="list", action="store_true",
            help="Produce a JSON consumable grouping of servers")
    parser.add_argument('--host', default=None, dest="host",
            help="Generate additional host specific details for given host")
    args = parser.parse_args()

    if args.list:
        print produce_json_object_list(scan_inv_directory())

    if args.host:
        print produce_json_object_host(scan_inv_directory(), args.host)