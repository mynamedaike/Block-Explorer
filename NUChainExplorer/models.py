from django.db import models

class BlockManager(models.Manager): 
    def addOne(self, number, hash, timestamp, miner, txNum, size, nonce, gasUsed, gasLimit, avgGasPrice, diff, totalDiff, reward, uncleReward, extraData):
        self.create(Number = number, Hash = hash, Timestamp = timestamp, Miner = miner, TxNum = txNum, Size = size, Nonce = nonce, GasUsed = gasUsed, GasLimit = gasLimit, AvgGasPrice = avgGasPrice, Difficulty = diff, TotalDifficulty = totalDiff, Reward = reward, UncleReward = uncleReward, ExtraData = extraData)
    
    def getAll(self):
        results = self.all().order_by('-id')
        return results
    
    def getOneByNum(self, blockNum):
        result = self.filter(Number__exact = blockNum)
        return result
    
    def getOneByHash(self, hash):
        result = self.filter(Hash__exact = hash)
        return result
    
    def getLatestNRows(self, Num):
        results = self.order_by('-id')[0:Num]
        return results

class Blocks(models.Model):
    Number = models.IntegerField() #The range is from -2147483648 to 2147483647. Is it enough?
    Hash = models.CharField(max_length = 66, unique = True)
    Timestamp = models.DateTimeField()
    Miner = models.CharField(max_length = 45)
    TxNum = models.IntegerField()
    Size = models.IntegerField()
    Nonce = models.CharField(max_length = 66)
    GasUsed = models.DecimalField(max_digits = 64, decimal_places = 0)
    GasLimit = models.DecimalField(max_digits = 64, decimal_places = 0)
    AvgGasPrice = models.DecimalField(max_digits = 64, decimal_places = 0)
    Difficulty = models.DecimalField(max_digits = 50, decimal_places = 0)
    TotalDifficulty = models.DecimalField(max_digits = 50, decimal_places = 0)
    Reward = models.DecimalField(max_digits = 20, decimal_places = 18)
    UncleReward = models.DecimalField(max_digits = 20, decimal_places = 18)
    ExtraData = models.CharField(max_length = 66)
    
    objects = BlockManager()
    
class TransactionManager(models.Manager):
    def addOne(self, txHash, blockNum, timestamp, status, fromAcc, toAcc, value, gasUsed, gasLimit, gasPrice, txFee, nonce):
        self.create(TxHash = txHash, BlockNum = blockNum, Timestamp = timestamp, Status = status, From = fromAcc, To = toAcc, Value = value, GasUsed = gasUsed, GasLimit = gasLimit, GasPrice = gasPrice, TxFee = txFee, Nonce = nonce)
    
    def getAll(self):
        results = self.all().order_by('-id')
        return results
    
    def getOne(self, txHash):
        result = self.filter(TxHash__exact = txHash)
        return result
    
    def getLatestNRows(self, Num):
        results = self.order_by('-id')[0:Num]
        return results
    
    def getAllByAddr(self, address):
        results = self.filter(models.Q(From__exact = address) | models.Q(To__exact = address)).order_by('-Timestamp')
        return results
    
    def getListByTimeRange(self, startTime, endTime):
        results = self.filter(Timestamp__range = (startTime, endTime))
        return results
    
class Transactions(models.Model):  
    TxHash = models.CharField(max_length = 66, unique = True)
    BlockNum = models.IntegerField() #The range is from -2147483648 to 2147483647. Is it enough?
    Timestamp = models.DateTimeField()
    Status = models.CharField(max_length = 45)
    From = models.CharField(max_length = 45)
    To = models.CharField(max_length = 45)
    Value = models.DecimalField(max_digits = 64, decimal_places = 6)
    GasUsed = models.DecimalField(max_digits = 64, decimal_places = 0)
    GasLimit = models.DecimalField(max_digits = 64, decimal_places = 0)
    GasPrice = models.DecimalField(max_digits = 64, decimal_places = 0)
    TxFee = models.DecimalField(max_digits = 64, decimal_places = 6)
    Nonce = models.CharField(max_length = 66)
    
    objects = TransactionManager()

class AccountManager(models.Manager):
    def addOne(self, address, balance, percentage, txNum, updatedTime, updatedFromBlock):
        self.create(Address = address, Balance = balance, Percentage = percentage, TxNum = txNum, UpdatedTime = updatedTime, UpdatedFromBlock = updatedFromBlock)
    
    def updateOne(self, address, balance, percentage, txNum, updatedTime, updatedFromBlock):
        self.filter(Address__exact = address).update(Balance = balance, Percentage = percentage, TxNum = txNum, UpdatedTime = updatedTime, UpdatedFromBlock = updatedFromBlock)
        
    def updateAllPercent(self, balanceSum):
        self.all().update(Percentage = models.F('Balance') / balanceSum)
    
    def getAll(self):
        results = self.all()
        return results
    
    def getOne(self, address):
        result = self.filter(Address__exact = address)
        return result
    
    def getLatestNRows(self, Num):
        results = self.order_by('-UpdatedTime')[0:Num]
        return results
    
    def getBalanceSum(self):
        result = self.all().aggregate(models.Sum('Balance'))['Balance__sum']
        return result

class Accounts(models.Model):
    Address = models.CharField(max_length = 45, unique = True)
    Balance = models.DecimalField(max_digits = 64, decimal_places = 6)
    Percentage = models.DecimalField(max_digits = 11, decimal_places = 10)
    TxNum = models.IntegerField()
    UpdatedTime = models.DateTimeField()
    UpdatedFromBlock = models.IntegerField()
    
    objects = AccountManager()
    
    
