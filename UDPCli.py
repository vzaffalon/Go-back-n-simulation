from socket import *
from Ack import *
from Message import *
import time
import json
import thread

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
timeBetweenPackets = 2 #tempo entre envio de pacotes em segundos
maximumPacketFlow = 70    #quantidade maxima de pacotes que a rede suporta ate ser considerada congestionada
numbersOfPacketsToBeTransmited = 45    #numero de mensagens que serao transmitidos pelo programa
messageString = "hello server "   #mensagem padrao que sera enviada

#parametros nao modificaveis
numbersOfPacketsTransmited = 0
sequenceNumber = 1       #numero de sequencia da mensagem
expectedSequenceNumber = 1 #numero do sequence number que o cliente espera receber do ack
window = []      #lista contendo elementos atualmente na janela
errorAlreadyOcurred = False  #evita que mensagems de error seja printada denovo pelos proximos acks da janela enviada
allWindowAckReceived = True

def receiveAck():
        ackSerialized, serverAddress = clientSocket.recvfrom(2048) #buffer size 2048
        ack = json.loads(ackSerialized)
        verifySequenceNumber(ack['sequenceNumber'],ack)

def verifySequenceNumber(seqNumber,ack):
    global expectedSequenceNumber,errorAlreadyOcurred
    if expectedSequenceNumber == seqNumber:
        if errorAlreadyOcurred == False: #verifica se os proximos acks devem ser ignorados ou nao
            print "Ack Recebido: " + '\n' + "Mensagem: "+ ack['data'] + '\n' + "sequenceNumber: " + str(ack['sequenceNumber']) + '\n'
            moveWindow()
    else:
        if errorAlreadyOcurred == False: #evita que mensagems de error seja printada denovo pelos proximos acks da janela enviada
            if seqNumber == -1:
                print 'timeout - ack do sequenceNumber ' + str(expectedSequenceNumber) + ' nao foi recebido - reenviando janela' + '\n'
                errorAlreadyOcurred = True
            else:
                print 'numero de sequencia errado da mensagem ' + ack['data'] + ' - irei reenviar mensagens posteriores da janela' + '\n'
                errorAlreadyOcurred = True
        else:
            print "Ack " + str(ack['sequenceNumber']) +' recebido e ignorado' +'\n'

def moveWindow():
    global expectedSequenceNumber,numbersOfPacketsToBeTransmited
    removeMessageFromWindow()           #mensagem enviada e com ack recebido retira da janela
    expectedSequenceNumber = expectedSequenceNumber + 1     #numero usado para verificacao de ordem

    if numbersOfPacketsTransmited <= numbersOfPacketsToBeTransmited:               #verifica se ainda existem pacotes a serem transmitidos
        addNewMessageToWindow()


def removeMessageFromWindow():
    window.pop(0)

def sendMessage(clientMessage):
    messageSerialization = json.dumps(clientMessage.__dict__)       #tranforma classe pra dicionario e manda em formato json
    clientSocket.sendto(messageSerialization,(serverIp, serverPort))
    print "Mensagem Enviada " + '\n' + "Mensagem: "+ clientMessage.data + '\n' + "sequenceNumber: " + str(clientMessage.sequenceNumber) + '\n'

def addNewMessageToWindow():
    global sequenceNumber
    clientMessage = Message(sequenceNumber,messageString + str(sequenceNumber))
    sequenceNumber = sequenceNumber + 1
    window.append(clientMessage)

def goBackExecutionThread():
    global window,timeBetweenPackets,numbersOfPacketsToBeTransmited,numbersOfPacketsTransmited,sequenceNumber,allWindowAckReceived
    #enquanto a janela nao fica vazia:
    #envia mensagens,recebe o ack,retira a primeira mensagem e adiciona a proxima na janela
    while len(window) > 0:
            #sincronize threads
            while(allWindowAckReceived == False):
                pass
            windowLen = len(window)
            windowAux = list(window)
            #create a instance of window so window changing on execution time dont mess with the program
            for y in range(0,windowLen):
                sendMessage(windowAux[y])                  #envia as mensagens da janela
                numbersOfPacketsTransmited = numbersOfPacketsTransmited + 1
                time.sleep(timeBetweenPackets)          #gera um tempo entre envio de pacotes


#there is no need for syncronization
#

def receiveAckThread():
    global errorAlreadyOcurred,window,timeBetweenPackets,allWindowAckReceived
    #enquanto a janela nao fica vazia:
    #envia mensagens,recebe o ack,retira a primeira mensagem e adiciona a proxima na janela
    while len(window) > 0:
        windowLen = len(window)
        errorAlreadyOcurred = False
        allWindowAckReceived = False
        for z in range(0,windowLen):
            time.sleep(timeBetweenPackets)          #gera um tempo entre envio de pacotes
            receiveAck()                            #recebe os ack da janela enviada
            if z == windowLen-1:
                allWindowAckReceived = True
                time.sleep(3)           #wait for goBackThread change of state when allWindowAckReceived = true



if __name__ == "__main__":
    #inicia a janela com as primeiras mensagens a serem enviadas
    for x in range (0,windowSize):
        addNewMessageToWindow()

    #create and start threads
    thread.start_new_thread(goBackExecutionThread, () )
    time.sleep(5)
    thread.start_new_thread(receiveAckThread,()),

    while 1:
        pass
    clientSocket.close()
