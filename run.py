from viewer.YouTube import YTViewer
import argparse

parser = argparse.ArgumentParser(
    prog = 'YouTube viewer',
    description = 'A program that helps you increase view count on youtube videos',
    epilog = 'Configure [stream.json] for video streaming',
    add_help = False
)

help_arg = """
Additional options available:
--keep-alive : Runs forever and loops all the located videos
--enable-gui : Chromedriver is visible
"""

parser.add_argument('--help', action='store_true')
parser.add_argument('--keep-alive', action='store_true', help='keeps the program running forever')
parser.add_argument('--enable-gui', action='store_true', help='visible gui')

if __name__ == '__main__':
    args = parser.parse_args()
    if args.help:
        print(help_arg)
    else:
        YTViewer(args.keep_alive, args.enable_gui).run()