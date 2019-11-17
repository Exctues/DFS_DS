from client.commands import Commands, Messages
from client.session import Session
import utils.parameters as parameters
from utils.constants import Constants
import utils.logger as logger

import argparse
import sys
import threading

interactive = len(sys.argv) == 1


class CommandAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings, dest, nargs, **kwargs)
        self.dest = dest
        self.__session = Session()

    def __call__(self, parser, namespace, values, option_string=None):

        command = getattr(Commands, values[0], None)
        if not command:
            logger.handle_error(Messages.wrong_command_message(values[0]))
            return

        if not command.validate_nargs(len(values) - 1):
            logger.handle_error(Messages.wrong_argnumber_message(command))
            return

        thread = threading.Thread(target=command, args=(self.__session, values[1:]))
        thread.start()
        thread.join()
        # command(self.__session, values[1:])


def setup_argparse():
    parser = argparse.ArgumentParser(
        usage=Messages.help_message()
    )

    parser.add_argument("command",
                        nargs=argparse.REMAINDER,
                        action=CommandAction)

    return parser


def interactive_loop(parser: argparse.ArgumentParser):
    while True:
        curr_command = input("> ").strip().split()
        if curr_command:
            parser.parse_args(curr_command)


def check_connection():
    try:
        import socket
        sock = socket.create_connection((Constants.NAMENODE_IP, Constants.CLIENT_TO_NAMENODE))
        sock.send('-100'.encode('utf-8'))
        # sock.shutdown(0)
        sock.close()

    except:
        logger.handle_error("Could not reach namenode server. Try again later.")
        exit(-1)


def main():
    if parameters.disable_color:
        logger.Colors.disable()

    parser = setup_argparse()

    if len(sys.argv) == 1:
        interactive_loop(parser)
    else:
        parser.parse_args()


if __name__ == '__main__':
    main()
