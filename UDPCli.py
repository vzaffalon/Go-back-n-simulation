from socket import *
from Ack import *
from Message import *
import time
import json
import thread
import sys

#socket config variables
serverIp = ''
serverPort = 12000
timeOut = 20     #em segundos

#client socket configuration
clientSocket = socket(AF_INET, SOCK_DGRAM)          #conexao socket tipo internet e udp
clientSocket.settimeout(timeOut)

#go-back-n variables
#parametros modificaveis
windowSize = 5   #janela do cliente

#parametros nao modificaveis
numbersOfPacketsToBeTransmited = 0    #numero de mensagens que serao transmitidos pelo programa
numbersOfPacketsTransmited = 0          #numero atual de pacotes ja transmitido
sequenceNumber = 1       #numero de sequencia da mensagem
expectedSequenceNumber = 1 #numero do sequence number que o cliente espera receber do ack
window = []      #lista contendo elementos atualmente na janela
errorAlreadyOcurred = False  #evita que mensagems de error seja printada denovo pelos proximos acks da janela enviada
extraPacketMode = False     #modo de envio de pacotes 1 por 1
acksToBeReceivedNumber = 0  #quantidades de acks que ainda serao recebidas
lastState = False       #ultimo estado: extraPacketMode ou modo janela
content = 0             # conteudo do arquivo
fileLine = 0            #variavel do arquivo
timeBetweenPackets = 2 #tempo entre envio de pacotes em segundos

def receiveAck():
        global acksToBeReceivedNumber
        ackSerialized, serverAddress = clientSocket.recvfrom(2048) #buffer size 2048
        ack = json.loads(ackSerialized)
        acksToBeReceivedNumber = acksToBeReceivedNumber - 1
        verifySequenceNumber(ack['sequenceNumber'],ack)

def showUploadDetails():
    global numbersOfPacketsTransmited,acksToBeReceivedNumber
    print "Numero de mensagens trasmitidas: " + str(numbersOfPacketsTransmited)
    print "Total de mensagens do arquivo: " + str(numbersOfPacketsToBeTransmited)
    print "Porcentagem do arquivo transferido: " + str((numbersOfPacketsTransmited/float(numbersOfPacketsToBeTransmited))*100.0) + '%\n'

def verifySequenceNumber(seqNumber,ack):
    global expectedSequenceNumber,errorAlreadyOcurred,extraPacketMode
    if expectedSequenceNumber == seqNumber:
            #print "ERROR ALREADY OCURRED " + str(errorAlreadyOcurred) + "lastState " + str(lastState)
            if (errorAlreadyOcurred == True):
                time.sleep(5)
                #print "UHUUUUUUU BIRLLLL"
            print "Ack Recebido: " + '\n' + "Mensagem: "+ ack['data'] + '\n' + "SequenceNumber: " + str(ack['sequenceNumber']) + '\n'
            errorAlreadyOcurred = False
            moveWindow()
    else:
        #print "expectedSequenceNumber" + str(expectedSequenceNumber) + '\n'
        extraPacketMode = False
        #print "error already ocurred" + str(errorAlreadyOcurred) + '\n'
        if errorAlreadyOcurred == False: #evita que mensagems de error seja printada denovo pelos proximos acks da janela enviada
            if seqNumber == -1:
                print 'Timeout - mensagem ' + ack['data'] + ' nao foi recebida - Reenviando janela' + '\n'
                errorAlreadyOcurred = True
            else:
                print 'Numero de sequencia errado da mensagem ' + ack['data'] + ' - Reenviando janela' + '\n'
                errorAlreadyOcurred = True
        else:
            print "Ack da mensagem: " + str(ack['data']) +' recebido e ignorado' +'\n'

def moveWindow():
    global expectedSequenceNumber,numbersOfPacketsToBeTransmited,extraPacketMode,numbersOfPacketsTransmited,windowSize
    removeMessageFromWindow()           #mensagem enviada e com ack recebido retira da janela
    expectedSequenceNumber = expectedSequenceNumber + 1     #numero usado para verificacao de ordem
    numbersOfPacketsTransmited = numbersOfPacketsTransmited + 1
    if numbersOfPacketsTransmited <= numbersOfPacketsToBeTransmited-windowSize:               #verifica se ainda existem pacotes a serem transmitidos
        addNewMessageToWindow()
        extraPacketMode = True

def removeMessageFromWindow():
    window.pop(0)

def sendMessage(clientMessage):
    global acksToBeReceivedNumber
    messageSerialization = json.dumps(clientMessage.__dict__)       #tranforma classe pra dicionario e manda em formato json
    clientSocket.sendto(messageSerialization,(serverIp, serverPort))
    print "Mensagem Enviada " + '\n' + "Mensagem: "+ clientMessage.data + '\n' + "SequenceNumber: " + str(clientMessage.sequenceNumber) + '\n'
    acksToBeReceivedNumber = acksToBeReceivedNumber + 1
    time.sleep(1)

def addNewMessageToWindow():
    global sequenceNumber,fileLine
    clientMessage = Message(sequenceNumber,content[fileLine])
    window.append(clientMessage)
    fileLine = fileLine + 1
    sequenceNumber = sequenceNumber + 1

def goBackExecutionThread():
    global window,timeBetweenPackets,extraPacketMode
    global sequenceNumber,acksToBeReceivedNumber,windowSize
    lastMessageSequenceNumber = x
    sub = 0
    #enquanto a janela nao fica vazia:
    #envia mensagens,recebe o ack,retira a primeira mensagem e adiciona a proxima na janela
    windowLen = len(window)
    while windowLen > 0:
            windowAux = window
            if extraPacketMode == False:
                while(extraPacketMode == False and acksToBeReceivedNumber > 0):
                    time.sleep(1)
                    pass
                if extraPacketMode == False:
                    y = 0
                    while y < windowLen:
                        try:
                            sendMessage(windowAux[y])
                            y = y + 1
                        except IndexError:
                            h = 5
            else:
                if numbersOfPacketsTransmited <= numbersOfPacketsToBeTransmited - windowSize:
                    y = windowSize-1 - sub
                    try:
                        if lastMessageSequenceNumber != windowAux[y].sequenceNumber:
                            lastMessageSequenceNumber = windowAux[y].sequenceNumber
                            sendMessage(windowAux[y])
                    except IndexError:
                        if numbersOfPacketsToBeTransmited - numbersOfPacketsTransmited == 1:
                            sendMessage(windowAux[y-1])
                        sub = sub + 1
                else:
                    y = windowSize - 1 - (windowSize - (numbersOfPacketsToBeTransmited - numbersOfPacketsTransmited))
                    if lastMessageSequenceNumber != windowAux[y].sequenceNumber and y >= 0:
                        lastMessageSequenceNumber = windowAux[y].sequenceNumber
                        sendMessage(windowAux[y])
                    sys.exit()
            windowLen = len(window)
    print "saiu"

def receiveAckThread():
    global errorAlreadyOcurred,window,timeBetweenPackets,extraPacketMode
    #enquanto a janela nao fica vazia:
    #envia mensagens,recebe o ack,retira a primeira mensagem e adiciona a proxima na janela
    windowLen = len(window)
    while windowLen > 0:
        time.sleep(timeBetweenPackets)          #gera um tempo entre envio de pacotes
        receiveAck()                            #recebe os ack da janela enviada
        windowLen = len(window)

    sys.exit("Arquivo transferido com sucesso!!")

def readFile(fname):
    global content,numbersOfPacketsToBeTransmited
    with open(fname) as f:
        content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    numbersOfPacketsToBeTransmited = len(content)

if __name__ == "__main__":
    readFile(raw_input("Escreva o nome do arquivo que sera transmitido: "))

    #inicia a janela com as primeiras mensagens a serem enviadas
    for x in range (0,windowSize):
        addNewMessageToWindow()

    #create and start threads
    thread.start_new_thread(goBackExecutionThread, () )
    time.sleep(5)
    thread.start_new_thread(receiveAckThread,()),

    while 1:
        time.sleep(8)
        showUploadDetails()
        if(numbersOfPacketsToBeTransmited == numbersOfPacketsTransmited):
            sys.exit()
        pass
    clientSocket.close()
