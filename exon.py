import socket


class Client(object):
    "Sends and receives message to and from the mess manager server."
    
    def __init__(self, host, port, timeout=1, packetSize=1024):
        self.connect(host, port)
        self.socket.settimeout(timeout)

    def connect(self, host, port):
        "Creates a  socket and connect to the server at the host:port address."
        self.socket = socket.socket()
        self.socket.connect((host, port))
    
    def formatMessage(self, command, parameters={}):
        message = command + " "
        for key in parameters:
            message += key + "::" + parameters[key]
        return message

    def parseMessage(self, data):
        string = data.decode('utf-8')
        return json.loads(string)        

    def sendMessage(self, func):
        def apiFunc(*args):
            message = func(*args)
            self.socket.send(message)
            data = self.socket.recv(self.packetSize)
            
        return apiFunc
        

    def getHelp(self):
        ""
        message = self.formatMessage("help")
        self.socket.send(message)        
        
    def getObject(self, ID):
        "Takes an ID and returns the corresponding object."
        message = self.formatMessage('id', {'id':ID})
        self.socket.send(message)

    def addNew(self, name, comments):
        pass

    def addComment(self, ID, comments):
        pass
    
    
