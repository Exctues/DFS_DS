import socket
import logger

# maybe also check distribute?


from storage.commands import CommandHandler

print("Started")
CommandHandler.handle_download_all((0, 0))
