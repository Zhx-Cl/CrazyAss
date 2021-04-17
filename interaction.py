"""
NAME:堡垒机
Author:DELL
DATE:2021/4/10
TIME:20:31
"""
import os, getpass
from django.contrib.auth import authenticate
import subprocess
from copy import deepcopy
import hashlib,time


def my_input(inp_dic):
    judge_dic = inp_dic.get('judge', {})
    choice_dic = inp_dic.get('choice', {})
    if judge_dic:
        reminder = judge_dic['reminder']
        yes = judge_dic['yes']
        no = judge_dic['no']

        while True:
            choice = input('%s' % reminder)
            if choice in [yes, no]:
                break
        if choice == yes:
            return True
        else:return False

    if choice_dic:
        pass
    else:
        pass


class Interaction:
    def __init__(self):
        self.user = authenticate(username='zhx@qq.com', password='zhx123123')

    def user_auth(self):
        index = 0
        while index < 3:
            username = input('username:').strip()
            if len(username) == 0: continue

            password = getpass.getpass('password:').strip()
            print(username, password)

            user = authenticate(username=username, password=password)

            if user:
                self.user=user
                break
            else:
                print('用户名或密码错误')
                index += 1
                continue

        else:
            print('输入密码次数超过三次')

    def interaction(self):
        # self.user_auth()
        record = []
        content = self.merge()
        record.append(deepcopy(content))
        while True:

            Interaction.display(content)
            choice = input(':').strip()
            if len(choice) == 0:
                continue

            if choice == 'q':
                break
            if choice == 'b':
                if len(record):
                    content = record[-1]
                    if len(record) != 1:
                        record.remove(record[-1])
                continue

            if choice == 'ms':
                ms = input('多选:')
                self.connect(self.translate(ms, content))
                continue

            if choice.isdigit():
                choice = int(choice)
                if choice >= len(content):
                    print('请合理输入!!')
                    continue
            else:
                print('请合理输入!!')
                continue
            try:  # 更换content的内容
                type_name = type(content[choice]).__name__
                if type_name == 'HostGroup':
                    record.append(deepcopy(list(content)))
                if type_name == 'str':
                    if choice == 1:
                        content = self.user.bind_hosts.all()
                    else:
                        content = self.user.host_group.all()
                    continue
                print('type:',type(content[choice]))
                content = content[choice].bind_hosts.all()

            except Exception as e:
                print(e)
                print('type:', type(content[choice]))
                self.connect(content[choice])


    def connect(self, bindHosts):
        if not isinstance(bindHosts, list):
            bindHosts = [bindHosts]
        for bindHost in bindHosts:

            if type(bindHost).__name__ == 'HostGroup':
                for i in bindHost.bind_hosts.all():
                    print('开始连接:', i)
                continue
            md5_str = hashlib.md5(str(time.time()).encode()).hexdigest()
            login_cmd = 'sshpass  -p {password} /usr/local/openssh7/bin/ssh {user}@{ip_addr} ' \
                        ' -o "StrictHostKeyChecking no" -Z {md5_str}'.format(password=bindHost.host_user.password,
                                                                             user=bindHost.host_user.username,
                                                                             ip_addr=bindHost.bind_host.ip_addr,
                                                                             md5_str=md5_str)
            subprocess.run(login_cmd, shell=True)

    @classmethod
    def display(cls, content):
        # 选择的是已经分好组

        for index, item in enumerate(content):
            print(index, item)

    def merge(self):
        '''合并'''

        ret = []
        ret.append('GroupHosts: %s' % self.user.host_group.count() )
        ret.append('UnGroupHosts: %s' % self.user.bind_hosts.count() )

        return ret

    @classmethod
    def translate(cls, choice_str, content):
        '''将列表转化成主机列表'''
        choice_str = choice_str.strip(',')
        choice_list = Interaction.str_to_list(choice_str, len(content))
        if not choice_list:
            return False
        bind_hosts = []

        for choice in choice_list:
            bind_hosts.append(content[choice])

        return bind_hosts

    @classmethod
    def str_to_list(cls, choice_str, length):
        '''将输入的字符串转化成数字列表'''
        choice_list = []
        str_list = choice_str.split(',')
        for index, i in enumerate(str_list):
            if i.isdigit():
                choice_list.append(int(i))
            else:
                inp_dic = {'judge': {'reminder': '第%s个数据: %s输入出现问题，是否过滤[y/n]:' % (index, i),
                                     'yes': 'y',
                                     'no': 'n'}}
                if my_input(inp_dic):
                    continue
                return []
        Interaction.examine(choice_list, length)
        return choice_list

    @classmethod
    def examine(cls, choice_list, length):
        '''检查是否超出索引'''
        if max(choice_list) >= length:

            inp_dic = {'judge': {'reminder': '检查到您输入含有超出索引的数值，是否过滤[y/n]:',
                                 'yes': 'y',
                                 'no': 'n'}}
            if my_input(inp_dic):
                while max(choice_list) >= length:
                    choice_list.remove(max(choice_list))
            else:
                return []


if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "堡垒机.settings")
    import django
    django.setup()
    obj = Interaction()

    obj.interaction()



