from socket import *
from Ack import *
from Message import *
import time
import json

def receiveAck():
        try:
            ackSerialized, serverAddress = clientSocket.recvfrom(2048) #buffer size 2048
            ack = json.loads(ackSerialized)
            print "Ack recebido: " + str(ack)
        except socket.timeout:
            print 'ack reception timed out'



def removeMessageFromWindow():
    window.pop(0)

def sendMessage(clientMessage):
    messageSerialization = json.dumps(clientMessage.__dict__)       #tranforma classe pra dicionario e manda em formato json
    clientSocket.sendto(messageSerialization,(serverIp, serverPort))
    print "Mensagem enviada: " + str(clientMessage.__dict__)

def addNewMessageToWindow():
    global sequenceNumber
    clientMessage = Message(sequenceNumber,messageString + str(sequenceNumber))
    window.append(clientMessage)
    sequenceNumber = sequenceNumber + 1


#socket config variables
serverIp = ''
serverPort = 12000
timeOut = 11     #em segundos

#client socket configuration
clientSocket = socket(AF_INET, SOCK_DGRAM)          #conexao socket tipo internet e udp
clientSocket.settimeout(timeOut)

#go-back-n variables
windowSize = 5   #janela do cliente
timeBetweenPackets = 1 #tempo entre envio de pacotes em segundos
packetsEmitedPerMinute = 60   #quantidade de pacotes emitidos por minuto
maximumPacketFlow = 70    #quantidade maxima de pacotes que a rede suporta ate ser considerada congestionada
expectedSequenceNumber = 0 #numero do sequency number que o cliente espera receber do ack
numbersOfPacketsToBeTransmited = 47    #numero de mensagens que serao transmitidos pelo programa
messageString = "hello server "   #mensagem padrao que sera enviada
sequenceNumber = 1       #numero de sequencia da mensagem
window = []      #lista contendo elementos atualmente na janela

#inicia a janela com as primeiras mensagens a serem enviadas
for x in range (0,windowSize):
    addNewMessageToWindow()

#enquanto a janela nao fica vazia:
#envia mensagens,recebe o ack,retira a primeira mensagem e adiciona a proxima na janela
while len(window) > 0:
        windowLen = len(window)
        for y in range(0,windowLen):
            sendMessage(window[y])
            time.sleep(timeBetweenPackets)          #gera um tempo entre envio de pacotes

        for z in range(0,windowLen):
            receiveAck()
            removeMessageFromWindow()           #mensagem enviada e com ack recebido retira da janela
            expectedSequenceNumber = expectedSequenceNumber + 1     #numero usado para verificacao de ordem

            if numbersOfPacketsToBeTransmited > 0:               #verifica se ainda existem pacotes a serem transmitidos
                addNewMessageToWindow()
                numbersOfPacketsToBeTransmited = numbersOfPacketsToBeTransmited - 1
            time.sleep(timeBetweenPackets)          #gera um tempo entre envio de pacotes



clientSocket.close()
