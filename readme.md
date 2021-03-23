# DNSPOD UPDATER
自动更新Dnspod域名解析记录的命令行工具，使用Python编写。

## 开始使用
在使用此程序之前，你需要在[dnspod.cn](https://dnspod.cn)上绑定域名，并创建解析记录。

+ **请注意：DNSPOD UPDATER只能修改已经存在的记录，不能添加或删除记录。**

1. 在[Release页面](https://github.com/YMNNs/DNSPOD_UPDATER/releases)下载二进制程序

2. 编辑```config.json```
   
   + 示例：
   ```json
   {
       "get_ipv6_method": "request",
       "get_ipv4_method": "request",
       "get_ipv6_request_url": "https://v6.ident.me/",
       "get_ipv4_request_url": "https://v4.ident.me/",
       "get_ipv6_command": "ipconfig /all",
       "get_ipv4_command": "",
       "get_domain_list_url": "https://dnsapi.cn/Domain.List",
       "get_record_list_url": "https://dnsapi.cn/Record.List",
       "get_qualified_record_type_url": "https://dnsapi.cn/Record.Type",
       "modify_record_url": "https://dnsapi.cn/Record.Modify",
       "close_timeout": 5
      }
   ```

   + ```get_ipv6_method```和```get_ipv4_method```分别是获取本机IPv6和IPv4的方法，可用选项有```request```（通过网络请求获取）和```command```（通过命令行获取）。

    **请注意：当系统启用了临时IPv6时，通过网络请求获取的IPv6地址是临时地址，系统防火墙会阻止全部传入连接。**

   + ```get_ipv6_request_url```和```get_ipv4_request_url```分别是通过网络请求获取本机IPv6和IPv4的URL，向该URL发送请求会直接返回本机的IPv6或IPv4地址。

   + ```get_ipv6_command```和```get_ipv4_command```分别是通过shell/cmd获取本机IPv6和IPv4的命令。

   + ```close_timeout```是程序运行结束后的退出倒计时，以秒为单位，当设置值小于0时程序结束后不退出。

   + 其余部分是Dnspod的API地址，无需修改。


3. 编辑```domains.json```

   + 示例：

     ```json
     { 
       "email": "your@ema.il",
       "params": {
         "login_token": "xxxxxx,xxxxxxxxxxxxxxxxxxx",
         "format": "json",
         "lang": "cn",
         "error_on_empty": "no"
       },
       "domains": [
         {
           "name": "example.com",
           "sub_domain": "@",
           "record_type": "A",
           "value": "$local_ipv4"
         },
         {
           "name": "example.com",
           "sub_domain": "www",
           "record_type": "AAAA",
           "value": "$local_ipv6"
         },
         {
           "name": "example.com",
           "sub_domain": "mirror",
           "record_type": "A",
           "value": "123.123.123.123"
         }
       ]}
     ```
     
   + ```email```: 你的电子邮件地址，仅用于向Dnspod发送请求的User-Agent。
   
   + ```login_token```: 请在[Dnspod密钥管理](https://docs.dnspod.cn/account/5f2d466de8320f1a740d9ff3/)中查看生成方法，完整的Token 是由 ID,Token 组合而成的，用英文的逗号分割。
   
   + ```lang```: Dnspod API语言，可用选项有```cn```和```en```。
   
   + ```domains```为列表格式，可以随意添加。对于单个```domains```项，有
   
     + ```name```: 域名，不包括主机记录
     + ```sub_domain```: 主机记录，若为空，请填写```@```，并与官网保持一致
     + ```record_type```: 记录类型，请保持与官网填写的一致，其中可能包含中文
     + ```value```: 记录值，需要与记录类型匹配，可用选项```$local_ipv6```（本机IPv6），```$local_ipv4```（本机IPv4），自定义值。
   + 请勿修改未提及的内容。
4. 保存上述所有文件，运```main.py```或```DNSPOD_UPDATER.exe```，如果运行中出现了错误，错误信息将会显示在屏幕上。
