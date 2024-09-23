# NetworkIntruder
This small utility can capture the current users of a network 
* save them to a sqlite file
* comapre against an already existing sqlite file
## Usage

1. capture mode, with ip range save the mac address of the current users
1. compare mode, //   // ///// comapre the mac address to the known users

```
$ python script.py capture 192.168.1.0/24
```

```
$ python script.py compare 192.168.1.0/24
```
