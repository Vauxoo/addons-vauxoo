#!/usr/bin/python

import sys
import os
from pprint import pprint


def parse_metadata(section):
    """Given the first part of a slide, returns metadata associated with it."""
    metadata = {}
    metadata_lines = section.split('\n')
    for line in metadata_lines:
        colon_index = line.find(':')
        if colon_index != -1:
            key = line[:colon_index].strip()
            val = line[colon_index + 1:].strip()
            metadata[key] = val
    messageList = section.split('\nmessage:')
    if len(messageList) == 2:
        metadata['message'] = messageList[1].strip()
    subMerges = []
    if metadata.get('message', ''):
        separator = \
            '    ------------------------------------------------------------\n'
        merges = metadata.get('message', '').split(separator)
        for m in merges:
            subMerges.append(parse_metadata(m))
    metadata['submerges'] = subMerges
    return metadata


def parse_file(filepath, logfromtext = False):
    separator =\
        '\n------------------------------------------------------------\n'
    sections = logfromtext and filepath or \
            open(filepath).read().split(separator)
    all_elements = []
    for s in sections:
        s_parsed = parse_metadata(s)
        pprint(parse_metadata(s), indent=2)
        all_elements.append(s)
    return all_elements
if __name__ == "__main__":
    '''
    This is the option if you need parse a file.
    '''
    if not len(sys.argv) == 2:
        section = '''
revno: 52 [merge]
revision-id: nhomae@gmail.com-20130416014106-o3n23he96s1pvaec
parent: nhomae@gmail.com-20130415213525-m1flejc57jr1op60
parent: julio@vauxoo.com-20130416010149-oex0miuij9t35a72
committer: Nhomar Hernandez <nhomae@gmail.com>
branch nick: xmind-openerp
timestamp: Mon 2013-04-15 21:11:06 -0530
message:

  [MERGE] Added given kanban wbs_codefield and off the field wbs
'''
        md = parse_metadata(section)
        print "Test Passed , It return %s " % str(md)
    else:
        filepath = sys.argv[1]
        if os.path.isfile(filepath):
            parse_file(filepath)
