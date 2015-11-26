import socket
import time, json


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
    
    def formatMessage(self, command, parameters={}):
        "Format a command and its parameters into a string understandable by the server."
        message = command
        if parameters != {}: message += " "
        formattedParameters = [key + "=\"" + parameters[key] + "\"" for key in parameters]
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
            #Send message and wait for reply
            sent = self.socket.send(message)
            if not sent: raise socket.error("The server closed the socket unexpectedly.")
            data = self.socket.recv(self.packetSize) #will fuck up if we dont limit message/comment & name size
            return self.parseMessage(data)
        return newCommand
        
    @executeCommand
    def getHelp(self):
        "Gets status information on the mess manager."
        return ('help', {})
        
    @executeCommand
    def getObject(self, ID):
        "Gets an object from its ID."
        return ('id', {'id':ID})

    @executeCommand
    def addNew(self, name, comments):
        "Adds a new object to the mess manager."
        return ('add new', {'name': name, 'comments': comments})

    @executeCommand
    def addComment(self, ID, comments):
        "Adds a new comment to existing object with ID."
        return ('add comment', {'id': ID, 'comments': comments})            

    
if __name__=='__main__':
    HOST = "hemochro.me"
    PORT = 8878

    try:
        ip = socket.gethostbyname(HOST)
    except socket.gaierror:
        print("Unable to resolve host.")
        exit(1)
        
    C = Client(ip, PORT)
    
