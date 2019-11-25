from utils.codes import Codes
import utils.logger as logger
import utils.parameters as parameters

import errors

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

        exit = "Leave the program"

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

        exit = ""

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
        exit = lambda n: True

    class Actions:
        @staticmethod
        def __n_args_handler(action, command, args):
            for arg in args:
                action(command, arg)

        @staticmethod
        def init(session, args):
            session.send_command(Commands.init)

        @staticmethod
        def __create_new_path(session, command, args):
            real_paths = list(map(session.resolve_full_path, args))
            for path in real_paths:
                if path:
                    errors.path_already_exists(path)
                    return

            args = list(map(session.resolve_partial_path, args))
            for path in args:
                if not path:
                    errors.path_invalid(path)
                    return

            CommandConfig.Actions.__n_args_handler(session.send_command, command, args)

        @staticmethod
        def make_file(session, args):
            CommandConfig.Actions.__create_new_path(session, Commands.make_file, args)

        @staticmethod
        def make_dir(session, args):
            CommandConfig.Actions.__create_new_path(session, Commands.make_dir, args)

        @staticmethod
        def print(session, args):
            source = session.resolve_full_path(args[0])
            if not source:
                errors.path_invalid(args[0])
                return

            is_dir = session.is_dir(source)
            if is_dir:
                errors.wrong_type(args[0], "file")
                return
            session.handle_print(Commands.print, source)

        @staticmethod
        def upload(session, args):
            if len(args) == 1:
                file_name = args[0].split(parameters.sep)[-1]

                args.append(file_name)

            args[1] = session.resolve_partial_path(args[1])

            if not args[1]:
                errors.path_invalid(args[1])
                return

            session.handle_upload(Commands.upload, args)

        @staticmethod
        def rm(session, args):
            args = list(map(session.resolve_full_path, args))
            for arg in args:
                if not arg:
                    errors.path_invalid(arg)

            is_dir = list(map(session.is_dir, args))
            for i, answer in enumerate(is_dir):
                if answer == 1:
                    errors.wrong_type(args[i], "file")
                    return

            CommandConfig.Actions.__n_args_handler(session.send_command, Commands.rm, args)

        @staticmethod
        def info(session, args):
            args = list(map(session.resolve_full_path, args))
            for arg in args:
                if not arg:
                    errors.path_invalid(arg)

            session.handle_info(Commands.info, args)

        @staticmethod
        def __copy_command(session, command, args):
            args[0] = session.resolve_full_path(args[0])
            path_exists = session.resolve_full_path(args[1])

            if path_exists:
                errors.path_already_exists(args[1])
                return

            args[1] = session.resolve_partial_path(args[1])
            for arg in args:
                if not arg:
                    errors.path_invalid(arg)
                    return

            session.send_command(command, *args)

        @staticmethod
        def copy(session, args):
            CommandConfig.Actions.__copy_command(session, Commands.copy, args)

        @staticmethod
        def move(session, args):
            CommandConfig.Actions.__copy_command(session, Commands.move, args)

        @staticmethod
        def cd(session, args):
            new_path = session.resolve_full_path(args[0])
            if not new_path:
                errors.path_invalid(new_path)
                return

            is_dir = session.is_dir(new_path)
            if not is_dir:
                errors.wrong_type(new_path, "directory")
                logger.handle_error(f"Path {new_path} is not a directory!")
                return

            session.change_curr_dir(new_path)

        @staticmethod
        def pwd(session, args):
            logger.print_info(session.get_curr_dir())

        @staticmethod
        def ls(session, args):
            if len(args) == 0:
                args.append(session.get_curr_dir())
            args[0] = session.resolve_full_path(args[0])
            if not args[0]:
                errors.path_invalid(args[0])
                return

            res = session.handle_ls(Commands.ls, args)
            if res is str:
                logger.print_info(res)
            else:
                logger.print_info('\n'.join(res))

        @staticmethod
        def rmdir(session, args):
            # validate and build paths
            args = list(map(session.resolve_full_path, args))
            for arg in args:
                if not arg:
                    errors.path_invalid(arg)
                    return

            is_dir = list(map(session.is_dir, args))
            for i, answer in enumerate(is_dir):
                if not answer:
                    errors.wrong_type(args[i], "directory")
                    return

            to_remove = []
            for dir in args:
                children = session.handle_ls(Commands.ls, [dir])

                if len(children) > 2:
                    logger.print_info("Directory {} is not empty. Do you want to remove it with all its contents?\n"
                                      "Print \"yes\" to proceed, or anything else to abort operation.".format(dir))
                    response = input()
                    if response.strip(" ") != "yes":
                        logger.print_info(f"Directory {dir} will not be removed")
                    else:
                        logger.print_info(f"Directory {dir} will be removed")
                        to_remove.append(dir)

                else:
                    to_remove.append(dir)

            CommandConfig.Actions.__n_args_handler(session.send_command, Commands.rmdir, to_remove)

        @staticmethod
        def help(session, args):
            if args:
                command = getattr(Commands, args[0], None)
                if not command:
                    logger.handle_error(Messages.wrong_command_message(args[0]))
                else:
                    logger.print_info("{}: {}\n{}".format(command.name, command.usage, command.description))
            else:
                logger.print_info(Messages.help_message())

        @staticmethod
        def exit(session, args):
            print("See ya!")
            exit(0)


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

    def __repr__(self):
        return str(self.code)


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
    exit = _Command("exit")

    @staticmethod
    def list():
        for member in dir(Commands):
            if member[:1] != '_' and member != 'list':
                yield _Command(member)
