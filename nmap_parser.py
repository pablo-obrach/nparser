#!/bin/usr/env python3

import argparse
import xml.etree.ElementTree as et
from termcolor import colored as color

banner = color(f"""
              ┍━━━━━━━━━━━━━━━━━━━━━━━━━━━━┑
                _  _ ___  _   ___  ___ ___ 
               | \| | _ \/_\ | _ \/ __| __|
               | .` |  _/ _ \|   /\__ \ _| 
               |_|\_|_|/_/ \_\_|_\|___/___|

              ┕━━━━━━━━━━━━━━━━━━━━━━━━━━━━┙
                      -Nmap Parse-
        Extract relevant information from Nmap= scan 

""", "green")

def parse_nmap_xml(file):
    tree = et.parse(file)
    root = tree.getroot()

    results = []
    closed_port = []

    # Getting the hosts
    for host in root.findall('host'):
        host_info = {}

        # Getting Host IP
        address = host.find('address')
        if address is not None:
            host_info['IP'] = address.get('addr')

        # Getting OS
        os = host.find('os')
        if os is not None:
            os_match = os.find('osmatch')
            if os_match is not None:
                host_info['OS'] = os_match.get('name')

        # Getting open Ports
        ports_info = []
        ports = host.find('ports')
        if ports is not None:
            for port in ports.findall('port'):
                port_info = {}
                state_element = port.find('state')
                if state_element is not None:
                    port_state =  state_element.get('state')
                    if port_state == 'closed':
                        closed_port.append(port.get('portid'))
                        host_info['closedports'] = len(closed_port)


                    if port_state == 'open':
                        port_info['portid'] = port.get('portid')
                        port_info['protocol'] = port.get('protocol')

                        service = port.find('service')
                        if service is not None:
                            port_info['service'] = service.get('name')
                            port_info['version'] = service.get('version')

                        ports_info.append(port_info)

        host_info['ports'] = ports_info
        results.append(host_info)

    return results

def print_results(results, banner):
    print(banner)
    for host in results:
        print(color(f"═══════════════════════════════════════════════════════════", "yellow"))
        print(color(f"\n[+] Host: {host.get('IP')}\n", "cyan"))

        if 'OS' in host:
            print(color(f"[+] OS: {host.get('OS')}\n", "blue"))
        
        print(color(f"[!] Closed Ports: {host.get('closedports')}\n", "red"))
        
        print(color(f"═══════════════════════════════════════════════════════════", "yellow"))
        print(f" ID/PROTOCOL      |      SERVICE       |      VERSION")
        print(color(f"═══════════════════════════════════════════════════════════\n", "yellow"))

        for port in host.get('ports',[]):
            print(color(f"- {port.get('portid')}/{port.get('protocol')}:\t\t{port.get('service', 'unknown')}\t\t\t{port.get('version', '')}", "magenta"))
        
        print(color(f"\n═══════════════════════════════════════════════════════════", "yellow"))


def main(file):
    results = parse_nmap_xml(file)
    print_results(results,banner)

if __name__ == '__main__':
    class CustomHelpFormatter(argparse.HelpFormatter):
        def add_usage(self, usage, actions, groups, prefix=None):
            if prefix is None:
                prefix = color('usage: ', "yellow")
            return super(CustomHelpFormatter, self).add_usage(usage, actions, groups, prefix)

        def format_help(self):
            return banner + super(CustomHelpFormatter, self).format_help()

    parser = argparse.ArgumentParser(
        description = color('Parse Nmap XML file and extract relevant information.', "yellow"),
        epilog = color('Example: python nmap_parser.py scan.xml', "yellow"),
        formatter_class = CustomHelpFormatter
    )
    parser.add_argument('file', help=color('Path to the Nmap XML file', "yellow"))

    args = parser.parse_args()
    main(args.file)

