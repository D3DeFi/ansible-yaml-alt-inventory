#!/usr/bin/env python

import os
import sys
import yaml
import argparse
try:
    import json
except:
    import simplejson as json

from ansible.plugins.inventory import detect_range, expand_hostname_range


def scan_inv_directory():
    """Function scans inventory directory for all files ending with .yml
    and tries to parse them into Python dict object."""
    invhosts = {}
    script_dir = os.path.dirname(os.path.realpath(__file__))
    invfiles = os.listdir(script_dir)

    # Scan every yml file found inside inventory directory
    for invfile in [x for x in invfiles if x.endswith('.yml')]:
        with open('{}/{}'.format(script_dir, invfile), 'r') as inventory:
            try:
                hosts = yaml.safe_load(inventory)
            except yaml.scanner.ScannerError as e:
                raise Exception('Inventory syntax error {}'.format(str(e.context_mark).lstrip()))

        # If there are hosts defined with range indicator [1:3], expand them
        hosts_expanded = {}

        if hosts:
            for key, val in hosts.iteritems():
                if detect_range(key):
                    key = expand_hostname_range(key)
                    hosts_expanded.update({x:val for x in key})
                else:
                    hosts_expanded[key] = val

        invhosts.update(hosts_expanded)

    if not invhosts:
        raise Exception('No hosts found inside inventory directory.')
    return invhosts


def produce_json_object_list(invhosts):
    """Function parses Python dictionary object representing YAML data
    and produces valid JSON object for Ansible."""
    inventory = {'_meta': {'hostvars': {}}}
    for key, val in invhosts.iteritems():
        groups = val.get('groups', None)
        if groups:
            groups = groups.replace(' ', '').split(',')
            for group in groups:
                if group in inventory.keys():
                    inventory[group].append(key)
                else:
                    inventory[group] = [key]

            inventory['_meta']['hostvars'][key] = val
        else:
            raise Exception('Unable to locate groups for {}. Maybe malformed or missing.'.format(key))

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
