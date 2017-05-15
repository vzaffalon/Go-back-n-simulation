from socket import *
from Ack import *
from Message import *
import time
import json
clientAddress = 0

def sendAck(sequenceNumber,data):
    ack = Ack(sequenceNumber,data + " ack")
    ackSerialization = json.dumps(ack.__dict__)  #envia o ack em formato json
    serverSocket.sendto(ackSerialization, clientAddress)
    print "Ack Enviado: " + str(ack.sequenceNumber)


def receiveMessage():
    global clientAddress
    messageSerialized, address = serverSocket.recvfrom(2048)
    clientAddress = address
    message = json.loads(messageSerialized)  #recebe a mensagem em formato json
    print "Mensagem recebida " + str(message)
    return message


#socket config variables
serverIp = ''
serverPort = 12000

#server socket configuration
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((serverIp, serverPort))
print 'The server is ready to receive'

timeBetweenAcksSend = 1

while 1:
    time.sleep(timeBetweenAcksSend)          #gera um tempo entre envio de pacotes
    message = receiveMessage()
    sendAck(message['sequenceNumber'],message['data'])
