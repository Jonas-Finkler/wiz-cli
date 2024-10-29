# wiz-cli
This is a simple command line interface to control wiz lights for the terminal. 

```
-> Bedroom     [x]  [================    ] 80%   [                    ] 2400K
   Bathroom    [x]  [================    ] 80%   [                    ] 2400K
   Kitchen     [ ]  [============        ] 60%   [========            ] 2850K
```

## Keybindings
| Key | Action |
| --- | ---    |
| `j`, `k` | Move cursor |
| `v` | Toggle selection |
| `c` | Clear selection |
| `<space>` | Toggle state |
| `h`, `l` | Change brightness |
| `u`, `i` | Change temperature |
| `q` | Exit |

## Configuration
The lights are configured in `~/.config/wiz/config.json` which lists lights as follows:
```json
{
  "Bedroom": {
    "ip": "192.168.1.20"
  },
  "Bathroom": {
    "ip": "192.168.1.31"
  },
  "Kitchen": {
    "ip": "192.168.1.30"
  },
}
```


