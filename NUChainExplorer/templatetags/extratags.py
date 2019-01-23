from django import template
from web3 import Web3
import time

register = template.Library()

@register.filter
def bytesToString(value):
    string = value.hex()
    return string

@register.filter
def truncate(value, length = 12, end = '...'):
    if(len(value) <= length):
        return value
    else:
        return value[0: length - len(end)] + end

@register.filter
def multiply(value1, value2):
    result  = value1 * value2
    return result

@register.filter
def divide(value1, value2):
    result = value1 / value2
    return result

@register.filter
def diffFormat(value):
    result = '%.3f' % (value / 1000000000000) + ' T'
    return result

@register.filter
def hashFormat(value):
    result = '%.3f' % (value / 1000000000000) + ' TH/s'
    return result

@register.filter
def gasFormat(value):
    result = str(value) + ' m/s'
    return result

@register.filter
def sizeFormat(value):
    result = '%.3f' % (value / 1000) + ' KB'
    return result

@register.filter
def dateFormat(value):
    result = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))
    return result

@register.filter
def amountFormat(value):
    result = '%.6f' % (Web3.fromWei(value, 'ether')) + ' ETH'
    return result

@register.filter
def priceFormat(value):
    result = '%.10f' % (Web3.fromWei(value, 'ether')) + ' ETH'
    return result
