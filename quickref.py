#!/usr/bin/env python3
"""
usage:
qr is a concise line-delimited cheatsheet reference CLI.
a `note` is a single line of text, containing anything you want.
a `comment` is any content after the first '#' on a line
a `cheatsheet` is a text file containing multiple notes, named like <topic>.txt
a `base path` is a folder containing multiple cheatsheets
configuration is done via an environment variable:
QR_DATA_DIR="/path/to/qr"
this directory can contain subdirectories (partially implemented)

$ qr
  show available quickref files (in $QR_DATA_DIR)
$ qr topic
  show all lines from all matching $QR_DATA_DIR/*/topic.txt
  a "topic" can be anything, but generally something like a language (py),
  application (blender), library/framework (django), command (git).
  also things like audio, pdf manipulation, CLI image editing.
$ qr topic pattern
  show all lines from topic.txt matching regex pattern
$ qr topic term1 term2 ...
  show all lines from topic.txt matching all terms
$ qr add topic "line with spaces"
  add "line with spaces" to topic.txt
$ qr edit [topic1 [topic2 [subdir/topic2 ...]]]
  open specified topics in $EDITOR; this file if no topics supplied.
$ qr alias topic shortcut
  create a new alias 'shortcut' for the topic 'topic' (not yet implemented)
"""
from collections import defaultdict
from pprint import pprint
import glob
import json
import logging
import os
import os.path
import re
import subprocess
import sys

# this is kind of kludgy - at first I used filesystem soft links for this purpose,
# but when I realized dropbox doesn't really support soft links, I stopped. I still
# wanted to support "alias" functionality, so I added this.
# aliases.json just contains a single json object containing KV pairs like "numpy": "py",
# where numpy is an alias for the file $QR/py.txt

log = logging.Logger('qr', level=logging.INFO)

aliases = {}
here = os.path.dirname(os.path.realpath(__file__))
alias_file = here + '/aliases.json'
if os.path.exists(alias_file):
    with open(alias_file) as f:
        aliases = json.load(f)


external_aliases = {}

PATHVAR_OLD = 'QR'
PATHVAR_NEW = 'QR_DATA_DIR'

qr_path = os.getenv(PATHVAR_OLD, 'undefined')
if qr_path != 'undefined':
    print('env var $%s is deprecated, update to $%s' %
          (PATHVAR_OLD, PATHVAR_NEW))

if qr_path == 'undefined':
    qr_path = os.getenv(PATHVAR_NEW, 'undefined')

if qr_path == 'undefined':
    qr_path = here + '/examples'
    print('no $%s var defined, using examples directory' % PATHVAR_NEW)

topic_map = defaultdict(list)  # {'name.txt': [fullpath1, fullpath2, ...], ...}
for root, dirs, files in os.walk(qr_path):
    for f in files:
        if f.endswith('.txt'):
            topic_map[f[:-4]].append('%s/%s' % (root, f))


def main(argv):
    if len(argv) == 1:
        # qr                         # show available topics
        print_tree(qr_path)

    elif argv[1] in ['h', 'help']:
        # qr help                    # show docstring
        print(__doc__)

    elif argv[1] in ['a', 'add']:
        # qr add topic "new line"    # add line to topic.txt
        # add line to topic.txt
        topic = expand_aliases(argv[2:3])[0]
        append_line_to_file(topic, argv[3])

    elif argv[1] in ['e', 'edit']:
        # qr edit [topic [topic      # edit topic.txt or qr.py
        topics = expand_aliases(argv[2:])
        open_files_for_editing(topics)

    elif argv[1] in ['al', 'alias']:
        create_alias(argv[2], argv[3])

    elif len(argv) == 2:
        # qr topic                   # show all lines of topic
        topic = expand_aliases(argv[1:2])[0]
        show_search_results(topic, '')

    else:
        # qr topic pattern [pattern  # show all lines matching patterns
        topic = expand_aliases(argv[1:2])[0]
        show_search_results(topic, argv[2:])


def expand_aliases(topics):
    # TODO: use 'external aliases' here... requires more effort though
    topics_out = []
    for topic in topics:
        if topic in aliases.keys():
            topics_out.append(aliases[topic])
        else:
            topics_out.append(topic)

    return topics_out


def get_aliases():
    return json.load(alias_file)


def save_aliases(aliases):
    json.dump(aliases, alias_file)


def create_alias(topic, shortcut, overwrite=False):
    # TODO: allow overwrite
    aliases = get_aliases()
    if shortcut in aliases:
        print('already exists!')
    aliases[shortcut] = topic


ignore_list = ['.git']


def print_tree(pth, level=1):
    if level == 1:
        print(pth)
    fds = os.listdir(pth)
    for d in fds:
        if d in ignore_list:
            continue
        if os.path.isdir(pth+'/'+d):
            print('%s%s/' % (2*level * ' ', d))
            print_tree(pth + '/' + d, level+1)
    for f in fds:
        if f.endswith('.txt'):
            print('%s%s' % (2*level * ' ', f))


def get_all_qr_filenames(aliases=False):
    # TODO: implement aliases=True here?
    return glob.glob(qr_path + '/**/*.txt', recursive=True)


def append_line_to_file(topic, line):
    log.debug('<append %s: `%s`>' % (qr_path+topic+'.txt', line))
    files = topic_map[topic]
    if len(files) <= 1:
        # if exactly one file found: append to this file
        # if no files found: create new file
        files = [qr_path + '/' + topic + '.txt']
    elif len(files) > 1:
        print('not adding; multiple matching topics found:')
        for f in files:
            print('  %s' % f)
        return

    with open(files[0], 'a') as f:
        f.write(line + '\n')


def open_files_for_editing(topics):
    if len(topics) == 0:
        # open this file
        fnames = [os.path.realpath(__file__)]
    else:
        # open all qr files for each specified topic
        fnames = [fname for arg in topics for fname in topic_map[arg]]

    if fnames == []:
        # create a new qr file
        fnames = [qr_path + '/' + t + '.txt' for t in topics]

    editor = os.getenv('EDITOR', 'undefined')
    if editor == 'undefined':
        editor = 'vim'
        print('$EDITOR not defined, using vim')

    for fname in fnames:
        cmd = '%s %s' % (editor, fname)
        print(cmd)
        subprocess.call(cmd, shell=True)


def show_search_results(topic, pattern_list):
    log.debug('<show_search_results %s: ' %
              (topic) + ' '.join(pattern_list) + '>')
    if topic == '.':
        show_results_from_all_files(pattern_list)
        return

    fnames = topic_map[topic]
    if len(fnames) == 0:
        print(topic, fnames)
        print("'%s' doesn't exist!\nsearching all qr files" % topic)
        # TODO: fuzzy match topic
        show_results_from_all_files([topic])
        # do something clever here?
        # maybe "(fname.*pattern|pattern.*fname)" ?
        return
    else:
        any_result = False
        for fname in fnames:
            res = search_file(fname, pattern_list)
            if res:
                any_result = True
                print('%s\n%s' % (fname, '=' * len(fname)))
                print(res)
        if not any_result:
            print('no results, searching all qr files')
            # would be nice to incorporate fname into pattern too...
            # maybe "(fname.*pattern|pattern.*fname)" ??
            show_results_from_all_files(pattern_list)


def show_results_from_all_files(pattern_list):
    log.debug('<show_results_from_all_files>')
    fnames = get_all_qr_filenames()
    for fname in fnames:
        res = search_file(fname, pattern_list)
        if res:
            print('\n%s\n%s' % (fname, '=' * len(fname)))
            print(res)


def search_file(fname, pattern_list):
    log.debug('<search_file %s>' % fname)
    res = []
    compiled_pattern_list = [re.compile(
        p, re.IGNORECASE) for p in pattern_list]
    with open(fname) as f:
        for line in f:
            print_flag = True
            for pattern in compiled_pattern_list:
                m = pattern.search(line)
                if not m:
                    print_flag = False

            if print_flag:
                res.append(line.rstrip())

    return '\n'.join(res)


if __name__ == '__main__':
    main(sys.argv)
