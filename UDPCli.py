from socket import *
from Ack import *
from Message import *
import time
import json

def receiveAck():
    ackSerialized, serverAddress = clientSocket.recvfrom(2048) #buffer size 2048
    ack = json.loads(ackSerialized)
    print "Ack recebido: " + str(ack)


def sendMessage(sequenceNumber):
    clientMessage = Message(sequenceNumber,messageString + str(messageNumber),timeOut)
    print "Mensagem enviada: " + str(clientMessage.__dict__)
    messageSerialization = json.dumps(clientMessage.__dict__)
    clientSocket.sendto(messageSerialization,(serverIp, serverPort))


#socket config variables
serverIp = ''
serverPort = 12000

#client socket configuration
clientSocket = socket(AF_INET, SOCK_DGRAM)          #conexao socket tipo internet e udp

#go-back-n variables
timeOut = 11     #em segundos
windowSize = 5   #janela do cliente
timeBetweenPackets = 1 #tempo entre envio de pacotes em segundos
packetsEmitedPerMinute = 60   #quantidade de pacotes emitidos por minuto
maximumPacketFlow = 70    #quantidade maxima de pacotes que a rede suporta ate ser considerada congestionada
expectedSequenceNumber = 0 #numero do sequency number que o cliente espera receber do ack
messageString = "hello server "   #mensagem padrao que sera enviada
messageNumber = 0       #numero da mensagem


while 1:
    for sequenceNumber in range(0, windowSize):
        sendMessage(messageNumber)
        receiveAck()
        messageNumber = messageNumber + 1
        expectedSequenceNumber = expectedSequenceNumber + 1
        time.sleep(timeBetweenPackets)

clientSocket.close()
