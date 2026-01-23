#!/usr/bin/env python3
"""
Unified CLI for novel-cli.
"""
import argparse
import sys
from pathlib import Path

from .config import DEFAULT_REF_AUDIO, DEFAULT_TTS_API
from .core import chapter, tts, volume
from .utils.text import DEFAULT_CHAPTER_PATTERN

def main():
    parser = argparse.ArgumentParser(
        description="Novel CLI: Tools for processing novel files.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Common arguments helper
    def add_common_args(p):
        p.add_argument('-f', '--file', required=True, type=Path, help="Path to input novel file.")
        p.add_argument('-r', '--regex-pattern', default=DEFAULT_CHAPTER_PATTERN, help=f"Regex for chapter detection.")

    # Subcommand: chapter (extract)
    parser_chapter = subparsers.add_parser('chapter', help='Extract specific chapters.')
    add_common_args(parser_chapter)
    parser_chapter.add_argument('-s', '--start-pattern', default=None, help="Start extraction from this chapter title substring.")
    parser_chapter.add_argument('-c', '--count', type=int, default=1, help="Number of chapters to extract.")

    # Subcommand: volume (mark)
    parser_volume = subparsers.add_parser('volume', help='Add volume markers.')
    add_common_args(parser_volume)
    parser_volume.add_argument('-n', '--interval', type=int, default=50, help="Chapters per volume (default: 50).")

    # Subcommand: tts
    parser_tts = subparsers.add_parser('tts', help='Synthesize audio for chapters.')
    add_common_args(parser_tts)
    parser_tts.add_argument('-s', '--start-pattern', default=None, help="Start TTS from this chapter title substring.")
    parser_tts.add_argument('-c', '--count', type=int, default=1, help="Number of chapters to synthesize.")
    parser_tts.add_argument('--api-url', default=DEFAULT_TTS_API, help=f"TTS API endpoint (default: {DEFAULT_TTS_API})")
    parser_tts.add_argument(
        '--ref-audio', 
        default=DEFAULT_REF_AUDIO, 
        help="Reference audio path on TTS server."
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        input_file = args.file
        if not input_file.exists():
            print(f"Error: File '{input_file}' not found.")
            sys.exit(1)
            
        if args.command == 'chapter':
            print(f"Extracting from: {input_file}")
            result = chapter.extract(
                input_path=input_file,
                start_pattern=args.start_pattern,
                count=args.count,
                regex_pattern=args.regex_pattern
            )
            if result:
                print(f"Success! Saved to: {result}")
            else:
                print("Error: Start chapter not found.")
                sys.exit(1)

        elif args.command == 'volume':
            print(f"Adding volume markers to: {input_file}")
            result = volume.add_markers(
                input_path=input_file,
                volume_step=args.interval,
                regex_pattern=args.regex_pattern
            )
            print(f"Success! Saved to: {result}")
            
        elif args.command == 'tts':
            print(f"Starting TTS for: {input_file}")
            result_dir = tts.process_tts(
                input_path=input_file,
                start_pattern=args.start_pattern,
                count=args.count,
                api_url=args.api_url,
                ref_audio_path=args.ref_audio,
                regex_pattern=args.regex_pattern
            )
            print(f"TTS processing complete. Output in: {result_dir}")

    except Exception as e:
        print(f"Error: {e}")
        # import traceback
        # traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
