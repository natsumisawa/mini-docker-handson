import linux
import os
import click
from typing import List

def hello(option: dict):
    command = option["commands"]

    print(f'this is child process. ${os.getpid()}') # same to parent pid number

    os.execvp(command[0], command) # exec command program from child process

def exec_run(commands: List[str]):
    print(f'run command called!')
    flags = 0
    option = {"commands": commands} # add other parameter after

    pid = linux.clone(hello, flags, (option,)) # system call
    print(pid) # print parent pid number
    os.waitpid(pid, 0)

    # ex) exec -> run echo hello
    # run command called!
    # hello