# Tor IP Rotation in Python
A simple Python script that requests new IPs from the Tor network.

Adapted from:
- *"[Crawling anonymously with Tor in Python](http://sacharya.com/crawling-anonymously-with-tor-in-python/)" by S. Acharya, Nov 2, 2013.*
- *[PyTorStemPrivoxy](https://github.com/FrackingAnalysis/PyTorStemPrivoxy) repo of [FrackingAnalysis](https://github.com/FrackingAnalysis)*

## Requirements
PS: **These are the requirments for Mac OS X**. You can find the requirements for Linux in [PyTorStemPrivoxy](https://github.com/FrackingAnalysis/PyTorStemPrivoxy).

### Tor
```shell
brew update
brew install tor
```

*Notice that the socks listener is on port 9050.*

Next, do the following:
- Enable the ControlPort listener for Tor to listen on port 9051, as this is the port to which Tor will listen for any communication from applications talking to the Tor controller.
- Hash a new password that prevents random access to the port by outside agents.
- Implement cookie authentication as well.

You can create a hashed password out of your password using:
```shell
tor --hash-password my_password
```

Then, update the `/usr/local/etc/tor/torrc` with the port, hashed password, and cookie authentication.
```shell
# content of torrc
ControlPort 9051
# hashed password below is obtained via `tor --hash-password my_password`
HashedControlPassword 16:E600ADC1B52C80BB6022A0E999A7734571A451EB6AE50FED489B72E3DF
CookieAuthentication 1
```

Restart Tor again to the configuration changes are applied.	
```shell
brew services restart tor
```

### Privoxy

Tor itself is not a http proxy. So in order to get access to the Tor Network, use `privoxy` as an http-proxy though socks5.

Install `privoxy` via the following command:
	
```shell
brew install privoxy
```

Now, tell `privoxy` to use TOR by routing all traffic through the SOCKS servers at localhost port 9050.
To do that append `/usr/local/etc/privoxy/config` with the following
```shell
forward-socks5t / 127.0.0.1:9050 . # the dot at the end is important
```

Restart `privoxy` after making the change to the configuration file.
```shell
brew services restart privoxy
```

### Stem

Next, install `stem` which is a Python-based module used to interact with the Tor Controller, letting us send and receive commands to and from the Tor Control port programmatically.

```shell
pip install stem
```

## Example Script

In the script below, `urllib` is using `privoxy` which is listening on port 8118 by default, and forwards the traffic to port 9050 on which the Tor socks is listening.

Additionally, in the `renew_connection()` function,  a signal is being sent to the Tor controller to change the identity, so you get new identities without restarting Tor. Doing such comes in handy when crawling a web site and one doesn't wanted to be blocked based on IP address.

```python
...

wait_time = 2
number_of_ip_rotations = 3
tor_handler = TorHandler()

ip = tor_handler.open_url('http://icanhazip.com/')
print('My first IP: {}'.format(ip))

# Cycle through the specified number of IP addresses via TOR
for i in range(0, number_of_ip_rotations):
    old_ip = ip
    seconds = 0

    tor_handler.renew_connection()

    # Loop until the 'new' IP address is different than the 'old' IP address,
    # It may take the TOR network some time to effect a different IP address
    while ip == old_ip:
        time.sleep(wait_time)
        seconds += wait_time
        print('{} seconds elapsed awaiting a different IP address.'.format(seconds))

        ip = tor_handler.open_url('http://icanhazip.com/')

    print('My new IP: {}'.format(ip))
```
Execute the Python 3 script above via the following command:
	
```shell
python main.py
```
When the above script is executed, one should see that the IP address is changing every few seconds.


## Changes from PyTorStemPrivoxy
- *Requirements for Mac OS X*
- *Python 3*
- *Coding style*
