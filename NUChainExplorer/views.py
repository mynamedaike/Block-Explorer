from NUChainExplorer.models import Blocks
from NUChainExplorer.models import Transactions
from NUChainExplorer.models import Accounts

from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import model_to_dict
import re
import json
import datetime
        
def paginateList(request, anyList):
    pageSize = request.GET.get('pageSize')
    pageNum = request.GET.get('pageNum')
    
    paginator = Paginator(anyList, pageSize)
          
    try:
        pageList = paginator.page(pageNum)
    except PageNotAnInteger:
        pageList = paginator.page(1)
    except EmptyPage:
        pageList = paginator.page(paginator.num_pages)
    
    return pageList

def getSerializedList(request, objList):
    totalNum = len(objList)
    pageList = paginateList(request, objList)
    pageList = [item['fields'] for item in json.loads(serializers.serialize('json', pageList))]
    return totalNum, pageList

def respondCoinPriceAndTxNumAndAccNum(request):
    coinPrice = 0
    txNum = Transactions.objects.getAll().count()
    accNum = Accounts.objects.getAll().count()
    
    return JsonResponse({'coinPrice': coinPrice, 'txNum': txNum, 'accNum': accNum})
    
def respondTxStatByDay(request, dayNum):
    txStat = []
    timeStr = (datetime.datetime.now()).strftime('%Y-%m-%d')
    zeroOfToday = datetime.datetime.strptime(timeStr, '%Y-%m-%d')
    for i in range(int(dayNum), 0, -1):
        startTime = zeroOfToday - datetime.timedelta(days = i)
        endTime = startTime + datetime.timedelta(days = 1)
        date = startTime.strftime('%Y-%m-%d')
        txNum = Transactions.objects.getListByTimeRange(startTime, endTime).count()
        txStat.append({'date': date, 'txNum': txNum})
    
    resParam = {'txStat': json.dumps(txStat)}
    return JsonResponse(resParam)
    
def respondBlockList(request):
    blocks = Blocks.objects.getAll()
    totalNum, pageList = getSerializedList(request, blocks)
    resParam = {'totalNum': totalNum, 'pageList': pageList}
    return JsonResponse(resParam)
    
def respondBlockDetail(request, blockNumOrHash):
    if blockNumOrHash.startswith('0x'):
        blocks = Blocks.objects.getOneByHash(blockNumOrHash)
    else:
        blocks = Blocks.objects.getOneByNum(blockNumOrHash)

    if blocks.count() != 0:
        resParam = {'block': model_to_dict(blocks[0])}
        return JsonResponse(resParam)
    else:
        return HttpResponse()
    
def respondTxList(request):
    transactions = Transactions.objects.getAll()
    totalNum, pageList = getSerializedList(request, transactions)
    resParam = {'totalNum': totalNum, 'pageList': pageList}
    return JsonResponse(resParam)
    
def respondTxDetail(request, txHash):
    transactions = Transactions.objects.getOne(txHash)
    if transactions.count() != 0:
        resParam = {'tx': model_to_dict(transactions[0])}
        return JsonResponse(resParam)
    else:
        return HttpResponse()
    
def respondAccList(request):
    accounts = Accounts.objects.getAll()
    totalNum, pageList = getSerializedList(request, accounts)
    resParam = {'totalNum': totalNum, 'pageList': pageList}
    return JsonResponse(resParam)

def respondAccDetail(request, address):
    accounts = Accounts.objects.getOne(address)
    if accounts.count() != 0:
        #######################################
        transactions = Transactions.objects.getAllByAddr(address)
        if transactions.count() != 0:
            totalNum, pageList = getSerializedList(request, transactions)
            resParam = {'acc': model_to_dict(accounts[0]), 'pageList': pageList}
        else:
            resParam = {'acc': model_to_dict(accounts[0])}        
        return JsonResponse(resParam)
    else:
        return HttpResponse()
    