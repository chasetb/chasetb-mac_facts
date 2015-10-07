#!/usr/bin/env python

##############################################################################
# Copyright 2014 Joseph Chilcote
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not
#  use this file except in compliance with the License. You may obtain a copy
#  of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
##############################################################################

## Warranty site
## https://selfsolve.apple.com/wcResults.do?sn=SERIAL&Continue=Continue&cn=&locale=&caller=&num=0

'''
Apple warranty lookup script.

This script scrapes Apple's warranty self serve site to determine whether a
given serial number is under warranty. Input can be one or more given
serial numbers, or a text file listing serials. Output can be standard out
or a CSV file.

usage: warranty [-h] [-v] [--quit-on-error] [-i INPUT] [-o OUTPUT] ...

positional arguments:
  serials

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         print output to console while writing to file
  --quit-on-error       if an error is encountered
  -i INPUT, --input INPUT
                        import serials from a file
  -o OUTPUT, --output OUTPUT
                        save output to a csv file

'''

import os
import sys
import subprocess
import plistlib
from dateutil import parser
import argparse
import urllib2

def get_asd_plist():
    '''Returns a dict containing model and asd version'''
    asd_plist = \
        'https://raw.githubusercontent.com/chilcote/warranty/master/com.github.chilcote.warranty.plist'
    response = urllib2.urlopen(asd_plist)
    return plistlib.readPlist(response)

def get_serial():
    '''Returns the serial number of this Mac'''
    print('Using this machine\'s serial number.')
    cmd = ['/usr/sbin/ioreg', '-c', 'IOPlatformExpertDevice', '-d', '2']
    output = subprocess.check_output(cmd)
    for line in output.splitlines():
        if 'IOPlatformSerialNumber' in line:
            return line.split(' = ')[1].replace('\"','')
    return None

def scrape_warranty_site(serial, graceful=True):
    '''Returns raw html from apple's warranty site'''
    url = 'https://selfsolve.apple.com/wcResults.do?sn={}&Continue=Continue&cn=&local=&caller=&num=0'.format(serial)
    warranty_status = urllib2.urlopen(url).read()

    model, date, status  = '', '', ''

    if 'serial number is not valid' in warranty_status:
        print('Serial number is not valid: {}'.format(serial))
        if not graceful:
            sys.exit(0)
    eligible = True
    for line in warranty_status.splitlines():
        if 'warrantyPage.warrantycheck.displayProductInfo' in line:
            model = line.split('displayProductInfo(')[1].split('\'')[3]
            if 'OBS,' in model:
                model = model.replace('OBS,','')
            if '~VIN,' in model:
                model = model.replace('~VIN,','')
        if 'warrantyPage.warrantycheck.displayEligibilityInfo' in line:
            if 'is not eligible' in line:
                eligible = False
    if eligible:
        for line in warranty_status.splitlines():
            if 'warrantyPage.warrantycheck.displayHWSupportInfo' in line:
                date = parser.parse(line.split('Date: ')[1].split('<br/')[0])
                status = line.split('Coverage: ')[1].split('\',')[0]
    else:
        date = parser.parse(line.split('Date: ')[1].split('<br/')[0])
        status = line.split('Coverage: ')[1].split('\',')[0]

    return model, date, status

def file_output(file, warranty_info):
    with open(file, 'a') as f:
        f.write('{},"{}",{},{},{}\n'.format(
            warranty_info[0],
            warranty_info[1],
            warranty_info[2],
            warranty_info[3])
        )

def warranty_output(warranty_info):
    print('mac_applecare_name=' + format(warranty_info[1]))
    print('mac_applecare_expiration=' + format(warranty_info[2]))

def main():
    '''Main method'''
    serials = []
    warranty = []
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='print output to console while writing to file', action='store_true')
    parser.add_argument('--quit-on-error', help='if an error is encountered', action='store_true')
    parser.add_argument('-i', '--input', help='import serials from a file')
    parser.add_argument('-o', '--output', help='save output to a csv file')
    parser.add_argument('serials', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.input:
        print('Importing serials from file: {}'.format(args.input))
        f = open(args.input, 'r')
        for line in f.read().splitlines():
            serials.append(line)
    elif args.serials:
        serials = args.serials
    else:
        serials.append(get_serial())
        if not serials[0]:
            print 'Error: Invalid or no serial number detected.'
            sys.exit(1)
    d = get_asd_plist()
    if args.output:
        print('Writing out to file: {}'.format(args.output))
        with open(args.output, 'w') as f:
            f.write('Serial Number,Product Description,Expires,Status,ASD Version\n')
    for serial in serials:
        if args.input:
            print('Processing: {}'.format(serial))
        (model, date, status) = scrape_warranty_site(serial, not args.quit_on_error)
        asd = 'Undetermined'
        for k, v in d.items():
            if model.upper() in k.upper():
                asd = v
                break
        warranty.append([serial.upper(), model, str(date).split(' ')[0], status, asd])
        if args.output:
            file_output(args.output, warranty[-1])
            if args.verbose:
                warranty_output(warranty[-1])
        else:
            warranty_output(warranty[-1])

if __name__ == '__main__':
    main()