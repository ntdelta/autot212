# AutoT212: Autopilot for Trading212

![practice account!!!](/assets/printer.png)
![practice account!!!](/assets/appsc.png)

## Overview

AutoT212 is a Python library that automates portfolio synchronization between the Autopilot app and Trading212 Pies. 

## Installation 

```
https://github.com/ntdelta/autot212.git
pip install .
```

## Running

```
autot212 --api-key "<TRADING 212 API KEY>"
```

## Automating

```
crontab -e
```

Run each night at 2am:
```
0 2 * * * /usr/bin/python3 -m autot212 --api-key "<TRADING 212 API KEY>" >> ~/t212_bot_log.log 2>&1
```


## Details

Steps towards reversing the Autopilot API are documented in the following blog post:

[https://blog.ntdelta.dev/2025-03-06-autopilot/](https://blog.ntdelta.dev/2025-03-06-autopilot/)