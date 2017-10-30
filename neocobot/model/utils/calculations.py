'''
@Project: Neocobot

@Created: 06-June-2017 by Chen Zhuo

Within this file, calculation functions are defined
'''
import math
import numpy
from numbers import Number

class BitFunctions:
    __qualname__ = 'BitFunctions'

    @staticmethod
    def check_bits(arg, bit=None):
        '''
        This function checks all the bits in 'bit' of all positive integers in 'arg' and returns bools or list of bools
        :param arg: positive integer or list of positive integers
        :param bit: positive integer or list of positive integers (or None)
        :return: booleans that represent if the bits of the arg integers are True (1) or False (0)
        '''
        if type(arg) is int:
            arg_type = 'int'
        elif type(arg) is list and False not in [type(arg_element) is int for arg_element in arg]:
            arg_type = 'list_of_int'
        elif type(arg) is dict and False not in [type(arg[arg_element]) is int for arg_element in arg]:
            arg_type = 'dict_of_int'
        else:
            print('ERROR: wrong type of argument "arg"')
            return
        if bit is None:
            bit_type = 'None'
        elif type(bit) is int:
            bit_type = 'int'
        elif type(bit) is list and False not in [type(bit_element) is int for bit_element in bit]:
            bit_type = 'list_of_int'
        else:
            print('ERROR: wrong type of argument "bit"')
            return
        if arg_type is 'int' and bit_type is 'int':
            return bool((arg >> bit) % 2)
        if arg_type is 'int' and bit_type is 'list_of_int':
            return [bool((arg >> bit_element) % 2) for bit_element in bit]
        if arg_type is 'int' and bit_type is 'None':
            bit_list = [x for x in range(math.floor(math.log2(arg) + 1))] if arg is not 0 else []
            return [bool((arg >> bit_element) % 2) for bit_element in bit_list]
        if arg_type is 'list_of_int' and bit_type is 'int':
            return [bool((arg_element >> bit) % 2) for arg_element in arg]
        if arg_type is 'list_of_int' and bit_type is 'list_of_int':
            return [[bool((arg_element >> bit_element) % 2) for bit_element in bit] for arg_element in arg]
        if arg_type is 'list_of_int' and bit_type is 'None':
            return_list = []
            for arg_element in arg:
                bit_list = [x for x in range(math.floor(math.log2(arg_element) + 1))] if arg_element is not 0 else []
                return_list.append([bool((arg_element >> bit_element) % 2) for bit_element in bit_list])
            return return_list
        if arg_type is 'dict_of_int' and bit_type is 'int':
            keys = [arg_element for arg_element in arg]
            values = [bool((arg[arg_element] >> bit) % 2) for arg_element in arg]
            return dict(zip(keys, values))
        if arg_type is 'dict_of_int' and bit_type is 'list_of_int':
            keys = [arg_element for arg_element in arg]
            values = [[bool((arg[arg_element] >> bit_element) % 2) for bit_element in bit] for arg_element in arg]
            return dict(zip(keys, values))
        if arg_type is 'dict_of_int' and bit_type is 'None':
            keys = [arg_element for arg_element in arg]
            values = []
            for arg_element in arg:
                bit_list = [x for x in range(math.floor(math.log2(arg[arg_element]) + 1))] if arg_element is not 0 else []
                values.append([bool((arg[arg_element] >> bit_element) % 2) for bit_element in bit_list])
            return dict(zip(keys, values))
        print('ERROR: this case actually should never happen')

class CheckTypes:
    __qualname__ = 'CheckTypes'

    @staticmethod
    def is_number(variable):
        return isinstance(variable, Number) and not isinstance(variable, bool)

    @staticmethod
    def is_list_of_numbers(variable, length=None):
        if type(variable) is list or type(variable) is numpy.ndarray:
            if length is not None and len(variable) != length:
                return False
            for value in variable:
                while not CheckTypes.is_number(value):
                    return False
            return True
        return False
