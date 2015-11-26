import socket
import time, json

HOST = "localhost"
PORT = 8878

class Client(object):
    "Sends and receives message to and from the mess manager server."
    
    def __init__(self, host, port, timeout=10, packetSize=1024):
        self.connect(host, port)
        self.socket.settimeout(timeout)
        self.packetSize = packetSize

    def connect(self, host, port):
        "Creates a  socket and connect to the server at the host:port address."
        self.socket = socket.socket()
        self.socket.connect((host, port))
    
    def formatMessage(self, command, parameters=[]):
        "Format a command and its parameters into a string understandable by the server."
        message = command
        if parameters != {}: message += " "
        formattedParameters = [key + "=\"" + value + "\"" for key, value in parameters]
        message += "::".join(formattedParameters)
        message += "\n" #End character for server
        return message.encode('utf-8')

    def parseMessage(self, data):
        "Transforms binary data into a json object."
        string = data.decode('utf-8')
        return json.loads(string)        

    #Could create commands fully dynamically but we'd lose on clarity
    def executeCommand(command):
        def newCommand(self, *args):
            #Create mesage
            commandId, commandArgs = command(self, *args)
            message = self.formatMessage(commandId, commandArgs)
            print(message)
            #Send message and wait for reply
            sent = self.socket.send(message)
            if not sent: raise socket.error("The server closed the socket unexpectedly.")
            data = self.socket.recv(self.packetSize) #will fuck up if we dont limit message/comment & name size
            return self.parseMessage(data)
        return newCommand
        
    @executeCommand
    def getHelp(self):
        "Gets status information on the mess manager."
        return ('help', [])
        
    @executeCommand
    def getObject(self, ID):
        "Gets an object from its ID."
        return ('id', [('id',ID)])

    @executeCommand
    def addNew(self, name, comments):
        "Adds a new object to the mess manager."
        return ('add new', [('name', name), ('comments', comments)])

    @executeCommand
    def addComment(self, ID, comments):
        "Adds a new comment to existing object with ID."
        return ('add comment', [('id', ID), ('comments', comments)])         

    
if __name__ == '__main__':
    import argparse, sys

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--add', nargs=3,
                        help='Can either add new or add comment using respectively name, comment and id, comment')
    parser.add_argument('--id')
    parser.add_argument('--host')
    parser.add_argument('--port', nargs=1)

    args = parser.parse_args(sys.argv[1:])
    if not args.add and not args.id:
        parser.error("At least one command required. See -h for usage.")
    if args.add and args.id:
        parser.error("Too many commands. See -h for usage.")

    host = args.host or HOST
    port = args.port or PORT
    
    #Check whether host is IP, if not resolve it
    try:
        socket.inet_aton(host)
    except socket.error:
        try:
            host = socket.gethostbyname(host)
        except socket.gaierror:
            print("Unable to resolve host.")
            exit(1)

    #Call command
    C = Client(host, port)
    if args.add:
        if args.add[0] == "new":
            print(C.addNew(args.add[1], args.add[2]))
            exit(0)
        elif args.add[0] == "comment":
            print(C.addComment(args.add[1], args.add[2]))
            exit(0)
        else:
            parser.error("Invalid argument for command add. See -h for usage help.")

    if args.id:
        if args.id:
            print(C.getObject(args.id))
            exit(0)
    
