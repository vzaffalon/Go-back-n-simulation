from socket import *
from Ack import *
from Message import *
import time
import json

#socket config variables
serverIp = ''
serverPort = 12000
timeOut = 5     #em segundos

#client socket configuration
clientSocket = socket(AF_INET, SOCK_DGRAM)          #conexao socket tipo internet e udp
clientSocket.settimeout(timeOut)

#go-back-n variables
#parametros modificaveis
windowSize = 5   #janela do cliente
timeBetweenPackets = 3 #tempo entre envio de pacotes em segundos
packetsEmitedPerMinute = 60   #quantidade de pacotes emitidos por minuto
maximumPacketFlow = 70    #quantidade maxima de pacotes que a rede suporta ate ser considerada congestionada
numbersOfPacketsToBeTransmited = 47    #numero de mensagens que serao transmitidos pelo programa
messageString = "hello server "   #mensagem padrao que sera enviada

#parametros nao modificaveis
sequenceNumber = 1       #numero de sequencia da mensagem
expectedSequenceNumber = 1 #numero do sequence number que o cliente espera receber do ack
window = []      #lista contendo elementos atualmente na janela
errorAlreadyOcurred = False  #evita que mensagems de error seja printada denovo pelos proximos acks da janela enviada

def receiveAck():
        ackSerialized, serverAddress = clientSocket.recvfrom(2048) #buffer size 2048
        ack = json.loads(ackSerialized)
        verifySequenceNumber(ack['sequenceNumber'],ack)

def verifySequenceNumber(seqNumber,ack):
    global expectedSequenceNumber,errorAlreadyOcurred
    if expectedSequenceNumber == seqNumber:
        if errorAlreadyOcurred == False: #verifica se os proximos acks devem ser ignorados ou nao
            print "Ack recebido: " + str(ack) + '\n'
            moveWindow()
        else:
            print "Ack " + str(ack) +' recebido e ignorado' +'\n'
    else:
        if errorAlreadyOcurred == False: #evita que mensagems de error seja printada denovo pelos proximos acks da janela enviada
            if seqNumber == -1:
                time.sleep(timeOut) #simula timeout
                print 'timeout - ack do sequenceNumber ' + str(expectedSequenceNumber) + ' nao foi recebido - reenviando janela' + '\n'
                errorAlreadyOcurred = True
            else:
                print 'numero de sequencia errado - reenviando janela' + '\n'
                errorAlreadyOcurred = True

def moveWindow():
    global expectedSequenceNumber,numbersOfPacketsToBeTransmited
    removeMessageFromWindow()           #mensagem enviada e com ack recebido retira da janela
    expectedSequenceNumber = expectedSequenceNumber + 1     #numero usado para verificacao de ordem

    if numbersOfPacketsToBeTransmited > 0:               #verifica se ainda existem pacotes a serem transmitidos
        addNewMessageToWindow()
        numbersOfPacketsToBeTransmited = numbersOfPacketsToBeTransmited - 1


def removeMessageFromWindow():
    window.pop(0)

def sendMessage(clientMessage):
    messageSerialization = json.dumps(clientMessage.__dict__)       #tranforma classe pra dicionario e manda em formato json
    clientSocket.sendto(messageSerialization,(serverIp, serverPort))
    print "Mensagem enviada: " + str(clientMessage.__dict__) + '\n'

def addNewMessageToWindow():
    global sequenceNumber
    clientMessage = Message(sequenceNumber,messageString + str(sequenceNumber))
    window.append(clientMessage)
    sequenceNumber = sequenceNumber + 1

#inicia a janela com as primeiras mensagens a serem enviadas
for x in range (0,windowSize):
    addNewMessageToWindow()

#enquanto a janela nao fica vazia:
#envia mensagens,recebe o ack,retira a primeira mensagem e adiciona a proxima na janela
while len(window) > 0:
        windowLen = len(window)
        errorAlreadyOcurred = False
        for y in range(0,windowLen):
            sendMessage(window[y])                  #envia as mensagens da janela
            time.sleep(timeBetweenPackets)          #gera um tempo entre envio de pacotes

        for z in range(0,windowLen):
            receiveAck()                            #recebe os ack da janela enviada
            time.sleep(timeBetweenPackets)          #gera um tempo entre envio de pacotes

clientSocket.close()
