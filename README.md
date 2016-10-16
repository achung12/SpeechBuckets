# Speech Buckets

Organize speech transcriptions into separate files by speaker


## Usage

` speech_buckets.py [-o OUTPUT_DIRECTORY] [-p OUTPUT_PREFIX] FILES
`


### positional arguments:

FILE(S)
>The file or directory (folder) of speech transcriptions to process.
If a directory is selected, speech_buckets.py will assume all files in
the directory are transcriptions and attempt to parse them




### optional arguments:

-o OUTPUT_DIRECTORY, --output-dir OUTPUT_DIRECTORY
>Choose the directory to write the output files to

-p OUTPUT_PREFIX, --prefix OUTPUT_PREFIX
>Provide a string that the output files will be prefixed with


## Example

Input file: debate.txt
```
CLINTON: I would blah blah blah.
Because blah.
SANDERS: Let me --
CLINTON: Blah blah.
SANDERS: Let me just say blah.
[applause]
```

Output file (1/2): debate_CLINTON.txt
```
I would blah blah blah.
Because blah.
Blah blah.
```

Output file (2/2): debate_SANDERS.txt
```
Let me --
Let me just say blah.
```