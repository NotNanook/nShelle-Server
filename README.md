```
        ____   _            _  _
 _ __  / ___| | |__    ___ | || |  ___
| '_ \ \___ \ | '_ \  / _ \| || | / _ \
| | | | ___) || | | ||  __/| || ||  __/
|_| |_||____/ |_| |_| \___||_||_| \___|
```

# nShelle-Server
This script is supposed to be run from the command line. E.g. `python main.py 127.0.0.1 5532`<br>

## Usage
When started successfully, you will see a prompt

### Commands for main prompt
- `help` or `h` for a list of all commands
- `clients` for a list of all currently connected clients
- `connect` or `c` to connect to a client by the id seen with the `clients` command

### Command for client prompt (after connecting)
- `quit` to disconnect from the current session
- `getClipboard` to get current clipboard data as string
- `whoami` to get PC name
- `screenshot` to take a screenshot from the client (uploaded to imgur)
- `shell` opens a normal cmd on the client (invisible)
