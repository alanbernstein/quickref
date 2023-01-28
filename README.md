Quickref is a simple CLI tool for interacting with a set of notes files. Use it to search for keywords by topic, and also to append lines of notes to the files.

## setup

It is currently just a single python file, which I use by including `#!/usr/local/bin/python`, and defining `alias qr="/path/to/quickref.py"`, because I like terse commands.

Define the environment variable `QR_DATA_DIR`, which should be a path containing text files, each named according to its topic, `topic.txt`.

Optionally, make sure your `EDITOR` environment variable is up to date, and qr will check that if you use the `qr edit` command.


### install script
```
mkdir -p $HOME/code/py
mkdir -p $HOME/cmd
mkdir -p $HOME/qr
git clone https://github.com/alanbernstein/quickref $HOME/code/py/quickref/
ln -s $HOME/code/py/quickref/quickref.py $HOME/cmd/qr # softlink version
# alias qr='$HOME/code/py/quickref/quickref.py # alias version

export QR_DATA_DIR="$HOME/qr"
git clone https://github.com/alanbernstein/cheatsheets $QR_DATA_DIR
```

## usage
Topic files are simple, line-based note snippets. The power of this tool is in creating these files yourself, one line at a time, and including the keywords that you are likely to remember yourself. Some examples are included (they are just reference tables translated to plaintext format).

`$ qr`
  show available quickref files (in `$QR_DATA_DIR`)
  
`$ qr topic`
  show all lines from `$QR_DATA_DIR/topic.txt` or `$QR_DATA_DIR/path/topic.txt`

a "topic" can be anything, but generally something like a language (py), application (blender), library/framework (django), command (git). also things like audio, pdf manipulation, CLI image editing.
  
`$ qr topic pattern`
  show all lines from `$QR_DATA_DIR/*/topic.txt` matching regex pattern

`$ qr path/topic pattern`
  show all lines from `$QR_DATA_DIR/path/topic.txt` matching regex pattern, omitting files from other subdirectories with matching names

`$ qr topic term1 term2 ...`
  show all lines from `$QR_DATA_DIR/topic.txt` matching all terms

`$ qr add topic "line with spaces"`
  add "line with spaces" to topic.txt

`$ qr edit [topic1 [topic2 ...]]`
  open specified topics in `$EDITOR`

`$ qr alias topic shortcut`
  create a new alias 'shortcut' for the topic 'topic' (not yet implemented)
