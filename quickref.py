#!/usr/bin/env python3
"""
usage:
qr is a concise line-delimited cheatsheet reference CLI.
a `note` is a single line of text, containing anything you want.
a `comment` is any content after the first '#' on a line
a `cheatsheet` is a text file containing multiple notes, named like <topic>.txt
a `base path` is a folder containing multiple cheatsheets
configuration is done via an environment variable:
QRPATH="/path/to/qr-1:/path/to/qr-2"
this is a list of paths, delimitied with colons, like $PATH, $GOPATH, etc.

$ qr
  show available quickref files (in $QR)
$ qr topic
  show all lines from $QR/topic.txt
  a "topic" can be anything, but generally something like a language (py),
  application (blender), library/framework (django), command (git).
  also things like audio, pdf manipulation, CLI image editing.
$ qr topic pattern
  show all lines from topic.txt matching regex pattern
$ qr topic term1 term2 ...
  show all lines from topic.txt matching all terms
$ qr add topic "line with spaces"
  add "line with spaces" to topic.txt
$ qr edit [topic1 [topic2 ...]]
  open specified topics in $EDITOR; this file if no topics supplied.
$ qr alias topic shortcut
  create a new alias 'shortcut' for the topic 'topic' (not yet implemented)
"""
import sys
import glob
import json
import os
import os.path
import subprocess
import re

# this is kind of kludgy - at first I used filesystem soft links for this purpose,
# but when I realized dropbox doesn't really support soft links, I stopped. I still
# wanted to support "alias" functionality, so I added this.
# aliases.json just contains a single json object containing KV pairs like "numpy": "py",
# where numpy is an alias for the file $QR/py.txt

aliases = {}
here = os.path.dirname(os.path.realpath(__file__))
alias_file = here + '/aliases.json'
if os.path.exists(alias_file):
    with open(alias_file) as f:
        aliases = json.load(f)


external_aliases = {}

qr_path = os.getenv('QR_DATA_DIR', 'undefined')
if qr_path == 'undefined':
    qr_path = os.getenv('QR', 'undefined')
    if qr_path != 'undefined':
        print('env var QR is deprecated, update to $QR_DATA_DIR')


if qr_path == 'undefined':
    qr_path = here + '/examples'
    print('no $QR path defined, using examples directory')


def main(argv):
    if len(argv) == 1:
        # qr                         # show available topics
        show_available_files()

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


def show_available_files():
    # print('<show available files>')
    fnames = get_all_qr_filenames()
    for f in fnames:
        print(f[len(qr_path) + 1:-4])


def get_all_qr_filenames(aliases=False):
    # TODO: implement aliases=True here?
    return glob.glob(qr_path + '/*.txt')


def append_line_to_file(topic, line):
    # print('<append %s: `%s`>' % (qr_path+topic+'.txt', line))
    with open(qr_path + '/' + topic + '.txt', 'a') as f:
        f.write(line + '\n')


def open_files_for_editing(topics):
    fnames = [os.path.realpath(__file__)]
    if len(topics) > 0:
        fnames = [qr_path + '/' + topic + '.txt' for topic in topics]

    editor = os.getenv('EDITOR', 'undefined')
    if editor == 'undefined':
        editor = 'vim'
        print('$EDITOR not defined, using vim')

    print(fnames)
    for fname in fnames:
        cmd = '%s %s' % (editor, fname)
        print(cmd)
        subprocess.call(cmd, shell=True)


def show_search_results(topic, pattern_list):
    # print('<search %s: ' % (qr_path+topic+'.txt') + ' '.join(pattern_list) + '>')

    if topic == '.':
        show_results_from_all_files(pattern_list)
        return

    fname = qr_path + '/' + topic + '.txt'
    if not os.path.isfile(fname):
        print(topic, fname)
        print("'%s' doesn't exist!\nsearching all qr files" % topic)
        # TODO: fuzzy match topic
        show_results_from_all_files([topic])
        # do something clever here?
        # maybe "(fname.*pattern|pattern.*fname)" ?
        return
    else:
        res = search_file(fname, pattern_list)
        if not res:
            print('no results, searching all qr files')
            # would be nice to incorporate fname into pattern too...
            # maybe "(fname.*pattern|pattern.*fname)" ??
            show_results_from_all_files(pattern_list)
        else:
            print(res)


def show_results_from_all_files(pattern_list):
    fnames = get_all_qr_filenames()
    for fname in fnames:
        res = search_file(fname, pattern_list)
        if res:
            print('\n%s\n%s' % (fname, '=' * len(fname)))
            print(res)


def search_file(fname, pattern_list):
    res = []
    compiled_pattern_list = [re.compile(p, re.IGNORECASE) for p in pattern_list]
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
