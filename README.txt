

记录 execv 的调用参数 通过UDP 发送给远程主机

仅仅是原型系统，使用请慎重。

使用方式：

一定要测试完备后再修改 /etc/ld.so.preload


测试：

编译后的 execv.so 放到 /usr/local/lib

export LD_PRELOAD=/usr/local/lib/execvlog.so
bash 新启动一个shell，这时所有执行的命令都会通过UDP发送到远程主机


正常使用：

如果工作正常，可以 vi /etc/ld.so.preload，增加一行
/usr/local/lib/execvlog.so    
上面这种方法会破坏docker 的运行，还下面得写法则docker 正常运行：
vi /etc/security/pam_env.conf 增加一行
LD_PRELOAD DEFAULT= OVERRIDE=/usr/local/lib/execvlog.so

