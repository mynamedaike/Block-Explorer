from __future__ import absolute_import, unicode_literals
from web3 import Web3
from decimal import Decimal
import time

from NUChain.celery import app
from NUChainExplorer.models import Blocks
from NUChainExplorer.models import Transactions
from NUChainExplorer.models import Accounts

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
    

def getBlockInfo(web3Connector, blockNumOrHash):
    block = web3Connector.eth.getBlock(blockNumOrHash)
    transactions = getAllTransactionsFromBlock(web3Connector, blockNumOrHash)
    blockInfo = {}
    blockInfo['number'] = block.number
    blockInfo['hash'] = block.hash.hex()
    blockInfo['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(block.timestamp))
    blockInfo['miner'] = block.miner
    blockInfo['txNum'] = web3Connector.eth.getBlockTransactionCount(blockNumOrHash)
    blockInfo['size'] = block.size
    blockInfo['nonce'] = block.nonce.hex()
    blockInfo['gasUsed'] = block.gasUsed
    blockInfo['gasLimit'] = block.gasLimit
    blockInfo['avgGasPrice'] = 0
    blockInfo['difficulty'] = block.difficulty
    blockInfo['totalDifficulty'] = block.totalDifficulty
    blockInfo['reward'] = 0
    blockInfo['uncleReward'] = 0
    blockInfo['extraData'] = block.extraData.hex()
    txFees = 0
    for tx in transactions:
        txFees += Decimal(tx.gas) * Decimal(tx.gasPrice) 
    blockInfo['reward'] = 3 + txFees / Decimal(1000000000000000000) + Decimal(3/32 * len(block.uncles)) #to be changed
    
    for uncle in block.uncles:
        blockInfo['uncleReward'] += (8 + web3Connector.eth.getBlock(uncle.hex()).number - block.number) * 3/8
        
    if blockInfo['gasUsed'] != 0:
        blockInfo['avgGasPrice'] = txFees / blockInfo['gasUsed'] / Decimal(1000000000)
        
    return blockInfo

def getTxInfo(web3Connector, txObject):
    txInfo = {}
    timestamp = web3Connector.eth.getBlock(txObject.blockNumber).timestamp
    txInfo['txHash'] = txObject.hash.hex()
    txInfo['blockNumber'] = txObject.blockNumber
    txInfo['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
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
    accInfo['txNum'] = Transactions.objects.getAllByAddr(address).count()
    accInfo['updatedTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    accInfo['updatedFromBlock'] = blockNum
    
    return accInfo

def writeBlocksToDB(web3Connector, currentBlockNum):
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
        for blockIndex in range(startIndex, currentBlockNum + 1):
            blocks.append(getBlockInfo(web3Connector, blockIndex))
         
        for block in blocks:
            Blocks.objects.addOne(block['number'], block['hash'], block['timestamp'], block['miner'], block['txNum'], block['size'], block['nonce'], block['gasUsed'], block['gasLimit'], block['avgGasPrice'], block['difficulty'], block['totalDifficulty'], block['reward'], block['uncleReward'], block['extraData'])
            count += 1
        
        print('Inserted ' + str(count) + ' blocks successfully!')
    
def writeTxsToDB(web3Connector, currentBlockNum):
    latestTx = None
    transactions = []
    count = 0
    
    if Transactions.objects.getLatestNRows(1):
        latestTx = Transactions.objects.getLatestNRows(1)[0]
        
    if latestTx and latestTx.BlockNum < currentBlockNum:
        startIndex = latestTx.BlockNum
    elif latestTx == None:
        startIndex = 1
    else:
        startIndex = None
    
    if startIndex != None:    
        for blockIndex in range(startIndex, currentBlockNum + 1):
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
        
    print('Inserted ' + str(count) + ' transaction records successfully!')
    
def writeAccsToDB(web3Connector, currentBlockNum):
    latestAddr = None
    count = 0
    
    if Accounts.objects.getLatestNRows(1):
        latestAddr = Accounts.objects.getLatestNRows(1)[0]
        
    if latestAddr and latestAddr.UpdatedFromBlock < currentBlockNum:
        startIndex = latestAddr.UpdatedFromBlock
    elif latestAddr == None:
        startIndex = 1
    else:
        startIndex = None
        
    if startIndex != None:    
        for blockIndex in range(startIndex, currentBlockNum + 1):
            addresses = getAllAddressesFromBlock(web3Connector, blockIndex)
        
            for address in addresses:
                accInfo = getAccInfo(web3Connector, address, blockIndex)
                if Accounts.objects.getOne(address).count() == 0:          
                    Accounts.objects.addOne(accInfo['address'], accInfo['balance'], accInfo['percentage'], accInfo['txNum'], accInfo['updatedTime'], accInfo['updatedFromBlock'])
                else:
                    Accounts.objects.updateOne(accInfo['address'], accInfo['balance'], accInfo['percentage'], accInfo['txNum'], accInfo['updatedTime'], accInfo['updatedFromBlock'])
                count += 1
        
        balanceSum = Accounts.objects.getBalanceSum()
        Accounts.objects.updateAllPercent(balanceSum)
        
        print(balanceSum)
        
        print('Inserted or updated ' + str(count) + ' accounts successfully!')

@app.task(name = 'writeDataToDB')
def writeDataToDB():
    web3Connector = Web3(Web3.HTTPProvider('http://localhost:8545'))
    currentBlockNum = web3Connector.eth.blockNumber
    
    writeBlocksToDB(web3Connector, currentBlockNum)
    writeTxsToDB(web3Connector, currentBlockNum)
    writeAccsToDB(web3Connector, currentBlockNum)
    