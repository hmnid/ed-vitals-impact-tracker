# TradeMeds

A tool for Elite Dangerous traders to track their cargo missions and trading sessions.

## Features

- **Session Summary**: See your trading activity for recent game sessions
- **Pending Cargo**: Track incomplete cargo missions across sessions
- **Automatic Journal Reading**: Works directly with Elite Dangerous journal files

## Installation

1. Make sure you have Python 3.10 or newer installed
2. Install Poetry:
   
   Bash:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
   
   PowerShell:
   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```

3. Clone this repository:
   ```powershell
   git clone https://github.com/yourusername/trademeds.git
   cd trademeds
   ```
4. Install dependencies:
   ```powershell
   poetry install
   ```

## Usage

The tool provides several commands:

### Show Recent Trading Sessions

```powershell
poetry run python -m trademeds sessions --sessions 5 --merges 0
```

Options:
- `--sessions`: Number of recent sessions to show (default: 5)
- `--merges`: Number of sessions to combine (useful when relogging during trade runs, default: 0)

### Show Pending Cargo Missions

```powershell
poetry run python -m trademeds pending-cargo --depth 10
```

Options:
- `--depth`: Number of recent sessions to analyze for missions (default: 10)

## Development

Run tests:
```powershell
poetry run test
```

Run type checking:
```powershell
poetry run check
```

Format code:
```powershell
poetry run format
```

Run all checks:
```powershell
poetry run lint
```

## Requirements

- Windows (currently only supports Windows journal path)
- Python 3.10+
- Elite Dangerous game with journal files

## License

MIT License - see LICENSE file for details