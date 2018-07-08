import time
from urllib.request import ProxyHandler, build_opener, install_opener, Request, urlopen

from stem import Signal
from stem.control import Controller


class TorHandler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}

    def open_url(self, url):
        # communicate with TOR via a local proxy (privoxy)
        def _set_url_proxy():
            proxy_support = ProxyHandler({'http': '127.0.0.1:8118'})
            opener = build_opener(proxy_support)
            install_opener(opener)

        _set_url_proxy()
        request = Request(url, None, self.headers)
        return urlopen(request).read().decode('utf-8')

    @staticmethod
    def renew_connection():
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password='btt')
            controller.signal(Signal.NEWNYM)
            controller.close()


if __name__ == '__main__':
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
