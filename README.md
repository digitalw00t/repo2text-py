# repo2text

A tool to convert GitHub repositories and documentation to text files.

## Installation

### Using pipx (recommended)

```bash
pipx install repo2text
```

### Using pip

```bash
pip install repo2text
```

## Usage

### Basic Usage

```bash
# Convert a local directory to text
repo2text .

# Convert a GitHub repository to text
repo2text -r https://github.com/username/repo

# Include documentation from a URL
repo2text -r https://github.com/username/repo -d https://docs.example.com

# Include token counts in file headers
repo2text -r https://github.com/username/repo -t

# Ignore specific file extensions
repo2text -r https://github.com/username/repo -i .log .tmp
```

### Command Line Options

- `-r, --repo`: GitHub repository URL
- `-d, --doc`: Documentation URL to include
- `-t, --token`: Include token count in file headers
- `-i, --ignore-extensions`: File extensions to ignore
- `--version`: Show version information

## Features

- Converts GitHub repositories to text files
- Includes documentation from URLs
- Supports token counting
- Ignores common binary and generated files
- Respects .gitignore patterns
- Splits large outputs into multiple files

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
