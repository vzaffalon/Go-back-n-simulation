from socket import *
from Ack import *
from Message import *
import time
import json
import random
import thread
import sys

#todo
#checksum
#caracter shift for generating error
#not sendind ack on case off ack lost
#envio de arquivo

#global variables
clientAddress = 0    #variavel que recebera endereco do cliente
randomChance = 10    #valor em porcentagem da chance de erros ocorrerem
timeBetweenAcksSend = 2   #tempo em segundos entre envio de acks
myFile = 0
timeOut = 10

dontSaveState = False
lastSequence = 9999

def sendAck(sequenceNumber,data):
    ack = Ack(sequenceNumber,data + " ack")
    ackSerialization = json.dumps(ack.__dict__)  #envia o ack em formato json
    serverSocket.sendto(ackSerialization, clientAddress)
    if sequenceNumber == -1:
        print "Ack com falha enviado: " + '\n' + "Mensagem: "+ ack.data + '\n' + "sequenceNumber: " + str(ack.sequenceNumber)  +  '\n'
    else:
        print "Ack enviado: " + '\n' + "Mensagem: "+ ack.data + '\n' + "sequenceNumber: " + str(ack.sequenceNumber)  + '\n'


def receiveMessage():
    global clientAddress,timeout
    try:
        messageSerialized, address = serverSocket.recvfrom(2048)
    except error as socketerror:
        print "Arquivo recebido e salvo em arquivoSaida.txt"
        myFile.close()
        sys.exit()
    clientAddress = address
    message = json.loads(messageSerialized)  #recebe a mensagem em formato json
    print "Mensagem Recebida: " + '\n' + "Mensagem: "+ message['data'] + '\n' + "sequenceNumber: " + str(message['sequenceNumber']) +  '\n'
    return message

def generateRandomChanceOfFail():
    global randomChance
    if random.randrange(0,100) < randomChance:
        return True
    else:
        return False

def verifyAckFailures(message):
    global dontSaveState,lastSequence
    if generateRandomChanceOfFail() == True and message['sequenceNumber'] != lastSequence:
        #envia mensagem com falha de ack ou seja sequenceNumber -1 gerando timeout
        sendAck(-1,message['data'] + " " +str(message['sequenceNumber']))
        if  dontSaveState == False:
            dontSaveState = True
            lastSequence = message['sequenceNumber']
    else:
        if generateRandomChanceOfFail() == True and message['sequenceNumber'] != lastSequence:
            #envia mensagem na ordem incorreta ou seja envia sequenceNumber errado
            sendAck(message['sequenceNumber'] + 1,message['data'] + " " +str(message['sequenceNumber']))
            if  dontSaveState == False:
                dontSaveState = True
                lastSequence = message['sequenceNumber']
        else:
            #nenhum erro envia mensagem normalmente com sequenceNumber correto
            sendAck(message['sequenceNumber'],message['data'] + " " +str(message['sequenceNumber']))
            if message['sequenceNumber'] == lastSequence:
                dontSaveState = False
            if dontSaveState == False:
                saveDataOnFile(message['data'])

def receiveAck():
    while 1:
        time.sleep(timeBetweenAcksSend)          #gera um tempo entre envio de pacotes
        message = receiveMessage()
        verifyAckFailures(message)


def createFile():
    global myFile
    myFile = open('arquivoSaida.txt', 'w')

def saveDataOnFile(fileData):
    global myFile
    myFile.write(fileData + '\n')
    print "Arquivo de saida recebeu: " + fileData + '\n'

if __name__ == "__main__":
    #socket config variables
    serverIp = ''
    serverPort = 12000

    #server socket configuration
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.settimeout(timeOut)
    serverSocket.bind((serverIp, serverPort))
    print 'The server is ready to receive' + '\n'

    createFile()
    #create and start threads
    thread.start_new_thread(receiveAck, ())

    while 1:
        pass
