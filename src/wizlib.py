import socket
import json
import curses
import os


TIMEOUT = 1.0
PORT = 38899
NRETRIES = 3
CONFIG_FILE = os.path.expanduser("~/.config/wiz/config.json")
TEMP_MIN = 2200
TEMP_MAX = 6500

class Lamp:
    def __init__(self, ip, name="NONAME"):
        self.ip = ip
        self.name = name
        self.temp = 2400
        self.dimming = 50
        self.state = False
        self.active = False

    def send_command(self, command, i_try=0):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(TIMEOUT)
        s.sendto(command.encode('utf-8'), (self.ip, PORT))
        response = None
        try:
            buffer_size = 1024
            response = b''
            while True:
                part, sender = s.recvfrom(buffer_size)
                response += part
                if len(part) < buffer_size:
                    break
        except socket.timeout:
            # print(f"No response from {self.ip}")
            ...
        finally:
            s.close()
            response = response.decode('utf-8', errors='ignore')
            try:
                response = json.loads(response)
                self.active = True
                return response
            except:
                if i_try < NRETRIES:
                    return self.send_command(command, i_try+1)
                else:
                    self.active = False
                    return None


    def get_status(self):
        command = json.dumps({
            "method": "getPilot",
            "params": {}
        })
        response = self.send_command(command)
        if response is None:
            return
        self.temp = response["result"]["temp"]
        self.dimming = response["result"]["dimming"]
        self.state = response["result"]["state"]

    def set_status(self, temp=None, dimming=None, state=None):
        if temp is not None:
            self.temp = temp
        if dimming is not None:
            self.dimming = dimming
        if state is not None:
            self.state = state

        command = json.dumps({
            "method": "setPilot",
            "params": {
                "temp": temp if temp is not None else self.temp,
                "dimming": dimming if dimming is not None else self.dimming,
                "state": state if state is not None else self.state
            }
        })
        response = self.send_command(command)

    @staticmethod
    def toBroadcastIp(ip):
        octs = ip.split(".")
        octs[3] = "255"
        return ".".join(octs)


# NOTE: Not working
def discoverBroadcast():
    ip = getLocalIp()
    msg = {
            "method": "getPilot",
            "params": {}
            # "method": "registration",
            # "params": {
            #     "id": 1,
            #     "phoneMac": "AAAAAAAAAAAA",
            #     "register": False,
            #     "phoneIp": "1.2.3.5",
            #     }
            }
    msg = json.dumps(msg)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # s.settimeout(TIMEOUT)
    # s.bind(("", PORT))
    s.sendto(msg.encode('utf-8'), (Lamp.toBroadcastIp(ip), PORT))
    s.settimeout(TIMEOUT)
    try:
        data, sender = s.recvfrom(1024)
        print("Received:", data.decode('utf-8', errors='ignore'))
        print("From:", sender)
    except socket.timeout:
        print(f"No response from broadcast")
        s.close()
    s.close()
    # listenThread.join()

def getLocalIp():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        return str(e)



def gui(stdscr, lamps):
    curses.noecho()
    curses.curs_set(0)
    stdscr.keypad(True)

    row = 0
    selected = [False for _ in lamps]
    namelen = max(len(l.name) for l in lamps)

    def draw():
        stdscr.clear()
        # stdscr.addstr(0, 0, "Wiz Light Control") 
        for i, l in enumerate(lamps):
            namepad = l.name.ljust(namelen)
            dimbar = "[" + "=" * (l.dimming // 5) + " " * (20 - l.dimming // 5) + "]"
            tbarmin = TEMP_MIN
            tbarmax = 3200
            tbarval = (l.temp - tbarmin) * 20 // (tbarmax - tbarmin)
            tempbar = "[" + "=" * tbarval + " " * (20 - tbarval) + "]"
            indicator_format = (curses.A_BOLD if selected[i] else curses.A_NORMAL) if row==i else curses.A_DIM
            stdscr.addstr(i+1, 0, f"{"->" if selected[i] or row==i else "  "}", indicator_format)
            stdscr.addstr(i+1, 3, f"{namepad}  [{'X' if l.state else ' '}]  {dimbar}{l.dimming:3d}%   {tempbar} {l.temp:4d}K", curses.A_DIM if not l.active else curses.A_NORMAL)

    def update_lamps(state=None, dimming=None, temp=None):
        for i, l in enumerate(lamps):
            if i == row or selected[i]:
                if not l.active:
                    l.get_status()
                    if not l.active:
                        continue
                l.set_status(state=state, dimming=dimming, temp=temp)   

    draw()
    while True:
        k = stdscr.getch()
        if k == ord('q'):
            break
        if k == ord('k'):
            row = max(0, row - 1)
        if k == ord('j'):
            row = min(len(lamps)-1, row + 1)
        if k == ord(' '):
            update_lamps(state=not lamps[row].state)
        if k == ord('h'):
            update_lamps(dimming=max(0, lamps[row].dimming - 5))
        if k == ord('l'):
            update_lamps(dimming=min(100, lamps[row].dimming + 5))
        if k == ord('u'):
            update_lamps(temp=max(TEMP_MIN, lamps[row].temp - 50))
        if k == ord('i'):
            update_lamps(temp=min(TEMP_MAX, lamps[row].temp + 50))
        if k == ord('v'):
            selected[row] = not selected[row]
        if k == ord('c'):
            selected = [False for _ in lamps]
        draw()

    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()




