BLOCK = "\u2588"
RESET = "\033[0m"

PALETTE = {
    ".": "\033[38;5;17m",    # background
    "K": "\033[38;5;232m",   # hat / hair
    "S": "\033[38;5;216m",   # skin
    "E": "\033[38;5;16m",    # eyes
    "M": "\033[38;5;88m",    # mouth
    "D": "\033[38;5;240m",   # coat
    "W": "\033[38;5;255m",   # shirt
    "R": "\033[38;5;124m",   # tie
}

DETECTIVE_VOSS_PORTRAIT = [
    "................................................",
    "..............KKKKKKKKKKKKKKKKKKKK..............",
    "............KKKKKKKKKKKKKKKKKKKKKKKK............",
    "..........KKKKKKKKKKKKKKKKKKKKKKKKKKKK..........",
    "..........KKKKKKKKKKKKKKKKKKKKKKKKKKKK..........",
    "............SSSSSSSSSSSSSSSSSSSSSSSS............",
    "...........SSSSSSSSSSSSSSSSSSSSSSSSSS...........",
    "...........SSSSSSEESSSSSSSSSSEESSSSSS...........",
    "...........SSSSSSEESSSSSSSSSSEESSSSSS...........",
    "...........SSSSSSSSSSSSSSSSSSSSSSSSSS...........",
    "...........SSSSSSSSSMMMMMMSSSSSSSSSSS...........",
    "............SSSSSSSSSSSSSSSSSSSSSSSS............",
    ".............SSSSSSSSSSSSSSSSSSSSSS.............",
    "..............DDDDDDDDDDDDDDDDDDDD..............",
    ".............DDDDDWWWWWWWWWWWWDDDDD.............",
    "............DDDDWWWWWWRRRRWWWWWWDDDD............",
    "...........DDDDDWWWWWWRRRRWWWWWWDDDDD...........",
    "...........DDDDDWWWWWWRRRRWWWWWWDDDDD...........",
    "...........DDDDDDDDDDDDDDDDDDDDDDDDDD...........",
    "...........DDDDDDDDDDDDDDDDDDDDDDDDDD...........",
    "............DDDDDDDDDDDDDDDDDDDDDDDD............",
    ".............DDDDDDDDDDDDDDDDDDDDDD.............",
    "................................................",
    "................................................",
]

def render_portrait(portrait):
    for row in portrait:
        print("".join(PALETTE[pixel] + BLOCK for pixel in row) + RESET)