"""
speech_buckets.py

Version: 1.0

Description: Parses transcriptions of speeches with multiple speakers into separate files (buckets)
             Requires Python 3.2 or higher

Author: Allen Chung <achung.dev[at]gmail[dot]com>

License: MIT
"""

import os
import sys


VERSION = 1.0
DEFAULT_OUTPUT_DIR = 'buckets'
DEFAULT_OUTPUT_PREFIX = ''


# Check if the given text is a name in the standard transcription format (all caps -- ex: SMITH)
# Input: String
# Output: True, if the string is a name
#         False, otherwise
def is_speaker_name(text):
    if text.isupper():
        if text.isalpha():
            return True
        elif "'" in text and text.count("'") == 1:
            # If the name has an apostrophe in it, remove it to be considered a name
            stripped = text.replace("'", '')
            return stripped.isalpha()
    return False


# Check if the speaker has annotations (ex: SMITH [shouting])
# Input: Part of the line that may be the speaker
# Output: True, if the input is indeed a speaker with annotations
#         False, otherwise
def is_speaker_annotated(speaker):
    if ' ' in speaker:
        space_index = speaker.index(' ')
        opening_punc = speaker[space_index + 1]
        closing_punc = speaker[-1]
        if (opening_punc == '(' or opening_punc == '[') and (closing_punc == ')' or closing_punc == ']'):
                return True
        return False


# Process the line of input by separating the name of the speaker and the spoken words, if appropriate
# Input: Line from speech transcription
# Output: Tuple of (SPEAKER, WORDS)
#         SPEAKER may be None if the speaker is the same as the previous line or the line represents an action
#         WORDS may be None if the line represents an action
def parse_transcription_line(line):
    line = line.strip()

    # Ignore actions
    if line == '' or (line[0] == '[' and line[-1] == ']') or (line[0] == '(' and line[-1] == ')'):
        return None, None
    if ': ' in line:
        space_index = line.index(' ')
        col_index = line.index(': ')
        if col_index:
            speaker_part = line[:col_index]
            spoken_part = line[col_index + 2:]
            if is_speaker_name(speaker_part):
                return speaker_part, spoken_part
            elif space_index < col_index:
                # Check if the speaker has an annotation
                if is_speaker_annotated(speaker_part):
                    speaker_part = line[:space_index]
                    if is_speaker_name(speaker_part):
                        return speaker_part, spoken_part
    # If the punctuation doesn't exist, there was no new speaker for this line
    return None, line


class TranscriptionParser:
    def __init__(self, target, output_dir=None, output_prefix=DEFAULT_OUTPUT_PREFIX):
        self.files_processed = 0
        self.files_created = 0

        self.target_dir = ''
        self.target_file = ''
        if os.path.exists(target):
            if os.path.isdir(target):
                self.target_dir = target
            else:
                self.target_dir, self.target_file = os.path.split(target)
        else:
            print('File "%s" does not exist!' % target)
            return

        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join(self.target_dir, DEFAULT_OUTPUT_DIR)

        self.output_prefix = output_prefix

    # Check if the given filename is a directory
    # If so, run the parser on each file in the directory
    # Otherwise, the filename is a file and should have the parser run on it
    def start(self):
        # Do nothing if no targets have been set
        if not self.target_dir and not self.target_file:
            return

        if not os.path.exists(self.output_dir):
            print('Creating output directory %s' % self.output_dir)
            os.makedirs(self.output_dir, exist_ok=True)

        if not self.target_file:
            # Parse the files in the directory, if only the directory was specified
            print('Processing files in %s' % self.target_dir)
            for filename in os.listdir(self.target_dir):
                transcription_file = os.path.join(self.target_dir, filename)
                if os.path.isfile(transcription_file):
                    self.process_transcription(transcription_file)
        else:
            self.process_transcription(os.path.join(self.target_dir, self.target_file))
        print('Finished! %d files processed; %d buckets created' % (self.files_processed, self.files_created))

    # Parse the file into buckets by speaker name and write them out to file
    def process_transcription(self, filepath):
        filename = os.path.split(filepath)[1]
        print('Processing file %s' % filename)

        # The buckets will be named <PREFIX><SPEECH_FILE>_<SPEAKER>.txt
        bucket_path = os.path.join(self.output_dir, self.output_prefix + filename[:filename.rindex('.')])

        # Store the file handles of the speakers' buckets
        file_handles = {}

        output_file = None
        with open(filepath, 'r') as speech_file:
            line_number = 0
            for line in speech_file:
                line_number += 1
                speaker, words = parse_transcription_line(line)
                if words:
                    # If there is a speaker, the speaker has changed -- get their output file
                    if speaker:
                        if speaker not in file_handles:
                            # Create the output file for this speaker
                            file_handles[speaker] = open('%s_%s.txt' % (bucket_path, speaker), 'w')
                            self.files_created += 1
                        # Grab the output file
                        output_file = file_handles[speaker]
                    if output_file:
                        # Write the line to the output file
                        output_file.write(words + '\r\n')
                    else:
                        # The speaker for this line was missed...
                        print('Missed speaker for line %d: %s' % (line_number, words))

        # Close all the files
        for key in file_handles:
            file_handles[key].close()

        self.files_processed += 1


if __name__ == '__main__':
    py_ver = sys.version_info
    if py_ver.major < 3:
        print('Please run this program with Python 3 or higher')
        sys.exit(1)
    elif py_ver.minor < 2:
        print('Please upgrade your installation of Python 3 to version 3.2 or higher')
        sys.exit(1)

    import argparse

    arg_parser = argparse.ArgumentParser(
        description='Organize speech transcriptions into separate files by speaker\n'
                    'Requires Python 3.2 or higher',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    arg_parser.add_argument(
        'file',
        metavar='FILE(S)',
        help=(
            'The file or directory (folder) of\n'
            'speech transcriptions to process.\n'
            'If a directory is specified, %(prog)s\n'
            'will assume all files in the directory are\n'
            'transcriptions and attempt to parse them.'
        )
    )
    arg_parser.add_argument(
        '-o', '--output-dir',
        metavar='DIRECTORY',
        help=(
            'Choose the directory to write the output files to\n'
            'Default: "buckets" in the same folder as the input'
        )
    )
    arg_parser.add_argument(
        '-p', '--output-prefix',
        metavar='PREFIX',
        default='',
        help=(
            'A string that the output files will be prefixed with\n'
            'Default: None'
        )
    )
    arg_parser.add_argument('--version', action='version', version='%(prog)s ' + str(VERSION))
    args = arg_parser.parse_args()

    TranscriptionParser(args.file, output_dir=args.output_dir, output_prefix=args.output_prefix).start()
