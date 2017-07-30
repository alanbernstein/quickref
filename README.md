Quickref is a simple CLI tool for interacting with a set of notes files. Use it to search for keywords by topic, and also to append lines of notes to the files.


## usage
`$ qr`
  show available quickref files (in $QR)
  
`$ qr topic`
  show all lines from $QR/topic.txt
  a "topic" can be anything, but generally something like a language (py), application (blender), library/framework (django), command (git). also things like audio, pdf manipulation, CLI image editing.
  
`$ qr topic pattern`
  show all lines from topic.txt matching regex pattern
  
`$ qr topic term1 term2 ...`
  show all lines from topic.txt matching all terms

`$ qr add topic "line with spaces"`
  add "line with spaces" to topic.txt

`$ qr edit [topic1 [topic2 ...]]`
  open specified topics in $EDITOR

`$ qr alias topic shortcut`
  create a new alias 'shortcut' for the topic 'topic' (not yet implemented)
