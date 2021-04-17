"""
NAME:堡垒机
Author:DELL
DATE:2021/4/11
TIME:9:07
"""
import copy


# for i in range(10):
#     li1.append(i)
#     li.append(copy.deepcopy(li1))
# a = {
#     'judge': {'reminder': '', 'is': '', 'no': ''},
#     'choice': {'reminder': '', 'choice_list': []}
# }

a = [1,2,3]
b = copy.deepcopy(a)
print(a == b)