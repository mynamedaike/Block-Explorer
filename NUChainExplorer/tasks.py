from __future__ import absolute_import, unicode_literals
from web3 import Web3
from decimal import Decimal
from django.utils.timezone import make_aware
from datetime import datetime
from celery_once import QueueOnce
from celery_once import AlreadyQueued
import time

from NUChain.celery import app
from NUChainExplorer.models import Blocks
from NUChainExplorer.models import Transactions
from NUChainExplorer.models import Accounts
from NUChainExplorer.models import UntilBlock

web3Connector = Web3(Web3.HTTPProvider('http://47.75.149.85:8545'))
#web3Connector = Web3(Web3.HTTPProvider('http://47.90.98.227:8545'))
#web3Connector = Web3(Web3.HTTPProvider('http://localhost:8545'))

def getAllTransactionsFromBlock(web3Connector, blockNumOrHash):
    transactions = []
    txCount = web3Connector.eth.getBlockTransactionCount(blockNumOrHash)
    for txIndex in range(txCount):
        tx = web3Connector.eth.getTransactionFromBlock(blockNumOrHash, txIndex)
        transactions.append(tx)
    return transactions 

def getAllAddressesFromBlock(web3Connector, blockNumOrHash):
    addresses = []
    transactions = getAllTransactionsFromBlock(web3Connector, blockNumOrHash)
    addresses.append(web3Connector.eth.getBlock(blockNumOrHash).miner)
    for tx in transactions:
        addresses.append(tx['from'])
        addresses.append(tx.to)
    return addresses

def getBlockModel(web3Connector, blockNumOrHash):
    block = web3Connector.eth.getBlock(blockNumOrHash)
    transactions = getAllTransactionsFromBlock(web3Connector, blockNumOrHash)
    
    number = block.number
    blockHash = block.hash.hex()
    timestamp = make_aware(datetime.utcfromtimestamp(block.timestamp))
    miner = block.miner
    txNum = web3Connector.eth.getBlockTransactionCount(blockNumOrHash)
    size = block.size
    nonce = block.nonce.hex()
    gasUsed = block.gasUsed
    gasLimit = block.gasLimit
    avgGasPrice = 0
    difficulty = block.difficulty
    totalDifficulty = block.totalDifficulty
    reward = 0
    uncleReward = 0
    extraData = block.extraData.hex()
    txFees = 0
    
    for tx in transactions:
        txFees += Decimal(tx.gas) * Decimal(tx.gasPrice) 
    reward = 5 + txFees / Decimal(1000000000000000000) + Decimal(5/32 * len(block.uncles)) #to be changed
    
    for uncle in block.uncles:
        uncleReward += (8 + web3Connector.eth.getBlock(uncle.hex()).number - block.number) * 5/8
        
    if gasUsed != 0:
        avgGasPrice = txFees / gasUsed / Decimal(1000000000)
        
    blockModel = Blocks(Number = number, Hash = blockHash, Timestamp = timestamp, Miner = miner, TxNum = txNum, Size = size, Nonce = nonce, GasUsed = gasUsed, GasLimit = gasLimit, AvgGasPrice = avgGasPrice, Difficulty = difficulty, TotalDifficulty = totalDifficulty, Reward = reward, UncleReward = uncleReward, ExtraData = extraData)
    
    return blockModel

def getTxInfo(web3Connector, txObject):
    txInfo = {}
    timestamp = web3Connector.eth.getBlock(txObject.blockNumber).timestamp
    txInfo['txHash'] = txObject.hash.hex()
    txInfo['blockNumber'] = txObject.blockNumber
    txInfo['timestamp'] = make_aware(datetime.utcfromtimestamp(timestamp))
    txInfo['status'] = '暂时没有这个参数'
    txInfo['from'] = txObject['from']
    txInfo['to'] = txObject.to
    txInfo['value'] = Decimal(txObject.value) / Decimal(1000000000000000000)
    txInfo['gasUsed'] = txObject.gas
    txInfo['gasLimit'] = web3Connector.eth.getBlock(txObject.blockNumber).gasLimit
    txInfo['gasPrice'] = txObject.gasPrice
    txInfo['txFee'] = Decimal(txInfo['gasUsed']) * Decimal(txInfo['gasPrice']) / Decimal(1000000000000000000)
    txInfo['nonce'] = txObject.nonce
    return txInfo

def getAccInfo(web3Connector, address, blockNum):
    accInfo = {}
    accInfo['address'] = address
    accInfo['balance'] = web3Connector.eth.getBalance(address)
    accInfo['percentage'] = 0
    accInfo['updatedTime'] = make_aware(datetime.utcnow())
    accInfo['updatedFromBlock'] = blockNum
    
    return accInfo

#@app.task(name = 'writeBlocksToDB', base = QueueOnce, once = {'graceful': True})
def writeBlocksToDB():
    print('[Blocks] Start writing blocks to the database!')
    currentBlockNum = web3Connector.eth.blockNumber
    latestBlock = None
    blocks = []
    count = 0
    
    if Blocks.objects.getLatestNRows(1):
        latestBlock = Blocks.objects.getLatestNRows(1)[0]
        
    if latestBlock and latestBlock.Number < currentBlockNum:
        startIndex = latestBlock.Number + 1
    elif latestBlock == None:
        startIndex = 1
    else:
        startIndex = None
        
    if startIndex != None:
        if startIndex  <= currentBlockNum - 99:
            endIndex = startIndex + 99
        else:
            endIndex = currentBlockNum
            
        for blockIndex in range(startIndex, endIndex + 1):
            blocks.append(getBlockModel(web3Connector, blockIndex))
            
        Blocks.objects.bulk_create(blocks)    
        
        print('[Blocks] Inserted ' + str(len(blocks)) + ' blocks successfully from Block ' + str(startIndex) + ' to Block ' + str(endIndex) + '!')
    else:
        print('[Blocks] The latest block is already in the database!')
    
    print('[Blocks] Finish writing blocks to the database!')

#@app.task(name = 'writeTxsToDB', base = QueueOnce, once = {'graceful': True})    
def writeTxsToDB():
    print('[Transactions] Start writing transactions to the database!')
    currentBlockNum = web3Connector.eth.blockNumber
    latestTx = None
    transactions = []
    count = 0
        
    if UntilBlock.objects.getOne():
        startIndex = UntilBlock.objects.getOne()[0].Number
    else:
        startIndex = 1
        UntilBlock.objects.addOne(1)  
    
    if startIndex  <= currentBlockNum - 99:
        endIndex = startIndex + 99
    else:
        endIndex = currentBlockNum
    
    for blockIndex in range(startIndex, endIndex + 1):
        transactions += getAllTransactionsFromBlock(web3Connector, blockIndex)
    
    for tx in transactions:
        if tx.blockNumber == startIndex:
            recorded = Transactions.objects.getOne(tx.hash.hex())
            if recorded.count() == 0:
                txInfo = getTxInfo(web3Connector, tx)
                Transactions.objects.addOne(txInfo['txHash'], txInfo['blockNumber'], txInfo['timestamp'], txInfo['status'], txInfo['from'], txInfo['to'], txInfo['value'], txInfo['gasUsed'], txInfo['gasLimit'], txInfo['gasPrice'], txInfo['txFee'], txInfo['nonce'])
                count += 1
        else: 
            txInfo = getTxInfo(web3Connector, tx)
            Transactions.objects.addOne(txInfo['txHash'], txInfo['blockNumber'], txInfo['timestamp'], txInfo['status'], txInfo['from'], txInfo['to'], txInfo['value'], txInfo['gasUsed'], txInfo['gasLimit'], txInfo['gasPrice'], txInfo['txFee'], txInfo['nonce'])
            count += 1
     
    if UntilBlock.objects.getOne()[0].Number != endIndex:
        UntilBlock.objects.updateOne(endIndex)
    
        if count != 0:
            print('[Transactions] Inserted ' + str(count) + ' transactions successfully from Block ' + str(startIndex) + ' to Block ' + str(endIndex) + '!')
        else:
            print('[Transactions] No transaction found from Block ' + str(startIndex) + ' to Block ' + str(endIndex) + '!')
    else:
        print('[Transactions] The latest transaction is already in the database!')
    
    print('[Transactions] Finish writing transactions to the database!')

#@app.task(name = 'writeAccsToDB', base = QueueOnce, once = {'graceful': True})
def writeAccsToDB():
    print('[Accounts] Start writing accounts to the database!')
    currentBlockNum = web3Connector.eth.blockNumber
    latestAddr = None
    count = 0
    
    if Accounts.objects.getLatestNRows(1):
        latestAddr = Accounts.objects.getLatestNRows(1)[0]
        
    if latestAddr:
        startIndex = latestAddr.UpdatedFromBlock
    else:
        startIndex = 1
    
    if startIndex  <= currentBlockNum - 99:
        endIndex = startIndex + 99
    else:
        endIndex = currentBlockNum
    
    for blockIndex in range(startIndex, endIndex + 1):
        addresses = getAllAddressesFromBlock(web3Connector, blockIndex)
        
        for address in addresses:
            accInfo = getAccInfo(web3Connector, address, blockIndex)
            if Accounts.objects.getOne(address).count() == 0:          
                Accounts.objects.addOne(accInfo['address'], accInfo['balance'], accInfo['percentage'], accInfo['updatedTime'], accInfo['updatedFromBlock'])
                count += 1
            elif Accounts.objects.getOne(address)[0]['UpdatedFromBlock'] != accInfo['updatedFromBlock']:
                Accounts.objects.updateOne(accInfo['address'], accInfo['balance'], accInfo['updatedTime'], accInfo['updatedFromBlock'])
                count += 1
        
    if count != 0:
        balanceSum = Accounts.objects.getBalanceSum()
        Accounts.objects.updateAllPercent(balanceSum)
    
        print('[Accounts] Inserted or updated ' + str(count) + ' accounts successfully from Block ' + str(startIndex) + ' to Block ' + str(endIndex) + '!')
    else:
        print('[Accounts] No account information needs updating!')
    
    print('[Accounts] Finish writing accounts to the database!')

@app.task(name = 'writeDataToDB', base = QueueOnce, once = {'graceful': True})
def writeDataToDB():
    writeBlocksToDB()
    writeTxsToDB()
    writeAccsToDB()
    