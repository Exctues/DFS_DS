from client.utils import *
from codes import Codes


class Messages:
    @staticmethod
    def help_message():
        help_message = "Command line interface for DFS\n\nPossible commands:\n"
        for command in Commands.list():
            help_message += "\t- " + command.name + ": " + command.description + "\n"
        help_message = help_message[:-2]

        return help_message

    @staticmethod
    def wrong_command_message(command):
        return "Command {} does not exist\n{}\n\n{}".format(command, "-" * 60, Messages.help_message())

    @staticmethod
    def wrong_argnumber_message(command):
        return "Wrong number of arguments\n{}\n\n{}\n".format("-" * 60, command.full_description())


class CommandConfig:
    class Description:
        cd = "Change current directory"
        pwd = "Print current working directory"

        init = "Initialize an empty repository (THIS WILL ERASE ALL EXISTING DATA ON THE DFS!)"

        make_file = "Create (a) new empty file(s)"
        print = "Print out contents of a file"
        upload = "Upload a file from host to the DFS"
        rm = "Remove (a) file(s)"
        info = "Get useful information on a file"
        copy = "Copy a file from source to destination"
        move = "Move a file from source to destination"

        ls = "List the contents of a directory"
        make_dir = "Create a new directory"
        rmdir = "Remove a directory (requires confirmation if the directory is not empty)"

        help = "Print help message"

    class Usage:
        init = ""

        cd = "<path>"
        pwd = ""

        make_file = "<file1> [<file2> <file3> ...]"
        print = "<file>"
        upload = "<host_filename> [<remote_filename>]"
        rm = "<file1> [<file2> <file3> ...]"
        info = "<file>"
        copy = "<source> <destination>"
        move = "<source> <destination>"

        ls = "[<path>]"
        make_dir = "<dir1> [<dir2> <dir3> ...]"
        rmdir = "<dir>"

        help = "[<command>]"

    class Validators:
        cd = lambda n: n == 1
        pwd = lambda n: n == 0

        init = lambda n: n == 0

        make_file = lambda n: n >= 1
        print = lambda n: n == 1
        upload = lambda n: 1 <= n <= 2
        rm = lambda n: n >= 1
        info = lambda n: n == 1
        copy = lambda n: n == 2
        move = lambda n: n == 2

        ls = lambda n: n <= 1
        make_dir = lambda n: n >= 1
        rmdir = lambda n: n >= 1

        help = lambda n: n <= 1

    class Actions:
        @staticmethod
        def __n_args_handler(action, command, args):
            for arg in args:
                res = action(command, arg)
                if not res:
                    handle_error("Command failed to execute for argument {} (and all the following)".format(arg))

        @staticmethod
        def init(session, args):
            session.send_command(Commands.init, [])

        @staticmethod
        def make_file(session, args):
            args = map(session.resolve_path, args)
            CommandConfig.Actions.__n_args_handler(session.send_command, Commands.make_file, args)

        @staticmethod
        def print(session, args):
            args = map(session.resolve_path, args)
            session.handle_upload(Commands.print, args[0])

        @staticmethod
        def upload(session, args):
            if len(args) == 1:
                args.append(args[0])

            args[1] = session.resolve_path(args[1])
            session.handle_upload(*args)

        @staticmethod
        def rm(session, args):
            args = map(session.resolve_path, args)
            CommandConfig.Actions.__n_args_handler(session.send_command, Commands.rm, args)

        # Todo add handler
        @staticmethod
        def info(session, args):
            args = map(session.resolve_path, args)
            session.send_command(Commands.info, args)

        @staticmethod
        def copy(session, args):
            args = map(session.resolve_path, args)
            session.send_command(Commands.copy, args)

        @staticmethod
        def move(session, args):
            args = map(session.resolve_path, args)
            session.send_command(Commands.move, args)

        @staticmethod
        def cd(session, args):
            session.change_curr_dir(args[0])

        @staticmethod
        def pwd(session, args):
            print_response(session.get_curr_dir())

        # Todo add handler
        @staticmethod
        def ls(session, args):
            if len(args) == 0:
                args.append(session.get_curr_dir())
            session.send_command(Commands.ls, args)

        @staticmethod
        def make_dir(session, args):
            CommandConfig.Actions.__n_args_handler(session.send_command, Commands.make_dir, args)

        @staticmethod
        def rmdir(session, args):
            CommandConfig.Actions.__n_args_handler(session.send_command, Commands.rmdir, args)

        @staticmethod
        def help(session, args):
            if args:
                command = getattr(Commands, args[0], None)
                if not command:
                    handle_error(Messages.wrong_command_message(args[0]))
                else:
                    print_response("{}: {}\n{}".format(command.name, command.usage, command.description))
            else:
                print_response(Messages.help_message())


class _Command:
    def __init__(self, name):
        self.__name = name
        self.__code = getattr(Codes, name)
        self.__description = getattr(CommandConfig.Description, name)
        self.__usage = name + " " + getattr(CommandConfig.Usage, name)
        self.__validate_nargs = getattr(CommandConfig.Validators, name)
        self.__action = getattr(CommandConfig.Actions, name)

    @property
    def name(self):
        return self.__name

    @property
    def code(self):
        return self.__code

    @property
    def description(self):
        return self.__description

    @property
    def usage(self):
        return self.__usage

    def full_description(self):
        return "usage: {}\n{}".format(self.__usage, self.__description)

    def validate_nargs(self, n):
        return self.__validate_nargs(n)

    def __call__(self, session, args):
        self.__action(session, args)

    def __str__(self):
        return self.__name


class Commands:
    cd = _Command("cd")
    pwd = _Command("pwd")
    init = _Command("init")
    make_file = _Command("make_file")
    print = _Command("print")
    upload = _Command("upload")
    rm = _Command("rm")
    info = _Command("info")
    copy = _Command("copy")
    move = _Command("move")
    ls = _Command("ls")
    make_dir = _Command("make_dir")
    rmdir = _Command("rmdir")
    help = _Command("help")

    @staticmethod
    def list():
        for member in dir(Commands):
            if member[:1] != '_' and member != 'list':
                yield _Command(member)
