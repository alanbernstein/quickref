Quickref is a simple CLI tool for interacting with a set of notes files. Use it to search for keywords by topic, and also to append lines of notes to the files.

## setup

It is currently just a single python file, which I use by including `#!/usr/local/bin/python`, and defining `alias qr="/path/to/quickref.py"`, because I like terse commands.

Define the environment variable `QR`, which should be a path containing text files, each named according to its topic, `topic.txt`.

Optionally, make sure your `EDITOR` environment variable is up to date, and qr will check that if you use the `qr edit` command.

## usage
Topic files are simple, line-based note snippets. The power of this tool is in creating these files yourself, one line at a time, and including the keywords that you are likely to remember yourself. Some examples are included (they are just reference tables translated to plaintext format).

`$ qr`
  show available quickref files (in `$QR`)
  
`$ qr topic`
  show all lines from `$QR/topic.txt`

a "topic" can be anything, but generally something like a language (py), application (blender), library/framework (django), command (git). also things like audio, pdf manipulation, CLI image editing.
  
`$ qr topic pattern`
  show all lines from `$QR/topic.txt` matching regex pattern
  
`$ qr topic term1 term2 ...`
  show all lines from `$QR/topic.txt` matching all terms

`$ qr add topic "line with spaces"`
  add "line with spaces" to topic.txt

`$ qr edit [topic1 [topic2 ...]]`
  open specified topics in `$EDITOR`

`$ qr alias topic shortcut`
  create a new alias 'shortcut' for the topic 'topic' (not yet implemented)
