# Novel CLI

A command-line tool for processing novel text files.

## Features

- **Chapter**: Extract specific chapters or efficient ranges from large novel files.
- **Volume**: Automatically insert volume markers every N chapters.
- **TTS**: Synthesize audio for chapters using GPT-SoVITS.

## Build & Run

### 1. Build Executable
Package the tool into a standalone executable (requires Python installed):

```bash
make build
```

This generates `dist/novel-cli.pyz`.

### 2. Run
You can run the generated executable directly:

```bash
# Show help
./dist/novel-cli.pyz --help
```

---

## Usage Examples

### Extract Chapters
```bash
# Extract 1 chapter starting from '第10章'
./dist/novel-cli.pyz chapter -f novel.txt -s "第10章" -c 1

# Extract 100 chapters from the beginning
./dist/novel-cli.pyz chapter -f novel.txt -c 100
```

### Add Volume Markers
```bash
# Add a volume marker every 50 chapters
./dist/novel-cli.pyz volume -f novel.txt -n 50
```

### Text-to-Speech (TTS)
Synthesize audio using a local GPT-SoVITS server.

```bash
# Process 5 chapters starting from '第10章'
./dist/novel-cli.pyz tts -f novel.txt -s "第10章" -c 5
```

## Configuration

You can configure defaults using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `NOVEL_CLI_TTS_API` | TTS API Endpoint | `http://127.0.0.1:9880/tts` |
| `NOVEL_CLI_REF_AUDIO` | Reference audio path on TTS server | (Empty) |

Example:
```bash
export NOVEL_CLI_TTS_API="http://myserver:9880/tts"
./dist/novel-cli.pyz tts -f novel.txt
```

## Structure

- `novel_cli/`: Source code (Flat layout).
- `tests/`: Unit tests.
- `Makefile`: Build automation.
