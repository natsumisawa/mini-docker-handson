import linux
import os
import click
from typing import List
import commands.cgroup as cgroup
import socket
import commands.local as local
import commands.data as data

def child_process(option: dict):
    # see pid is same to parent process
    # but when receive CLONE_NEWPID, is different!!! > $1
    pid = os.getpid()
    print(f'this is child process. {pid}')

    image = option["image"]
    container = option["container"]

    # mount pulled dirs (=image) as overlayfs (4-2)
    linux.mount(
        'overlay',
        container.root_dir,
        'overlay',
        linux.MS_NODEV,
        f"lowerdir={image.content_dir},upperdir={container.rw_dir},workdir={container.work_dir}"
    )

    print('finish mount!!')

    limit = option["limit"]
    if limit:
        cg = cgroup.CGroup("newcgroup?")
        cg.set_cpu_limit(limit)
        cg.add(pid)

    # edit hostname from child process (3-2)
    linux.sethostname('container-process')

    # exec received command program from child process (1-2)
    command = option["commands"]
    command = command if len(command) > 0 else image.cmd

    # change root dir (3-3)
    print(container.root_dir)
    os.chroot(container.root_dir)
    os.chdir("/")

    print(command[0])
    print(command)
    os.execvp(command[0], command)


def exec_run(image_name: str, limit: float, commands: List[str]):

    # flags = linux.CLONE_NEWUTS # devide UTS namespace
    flags = linux.CLONE_NEWPID # devide PID namespace

    image_list = local.find_images()
    image = next((v for v in image_list if v.name == f'library/{image_name}'), None)
    print(f'found image : {image}')

    container = data.Container.init_from_image(image)

    print(container)

    option = {"commands": commands, "limit": limit, "container": container, "image": image}

    pid = linux.clone(child_process, flags, (option,)) # system call
    print(pid) # print parent pid number

    os.waitpid(pid, 0) # wait done child process

    # ex) exec -> run echo hello
    # run command called!
    # hello