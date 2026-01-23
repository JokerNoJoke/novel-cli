"""
Configuration for novel-cli.

Supports environment variables for customization.
"""
import os

# TTS API endpoint
DEFAULT_TTS_API = os.getenv("NOVEL_CLI_TTS_API", "http://127.0.0.1:9880/tts")

# Reference audio path for TTS (on TTS server)
DEFAULT_REF_AUDIO = os.getenv("NOVEL_CLI_REF_AUDIO", "/Users/joker/privateProjects/python/GPT-SoVITS/output/slicer_opt/刘亦菲资生堂独家专访_Vocals.flac_0000409920_0000612160.wav")
