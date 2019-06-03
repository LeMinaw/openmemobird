"""
Memobird-oriented classes.
"""


class Memobird:

    def __init__(self, host='192.168.10.1', port='80'):
        """Creates a Memobird instance. <host> is Memobird IP adress or hostname. If not
        provided, the program will attempt to connect to the Memobird in 'local mode',
        where it acts as a local WiFi network. The <port> can also be changed, it may be
        useful if you want to access your memobird behind a NAT."""
        
        self.host = host
        self.port = port
    
    @property
    def uri(self):
        """Returns the URI to send data to the Memobird."""
        
        return f"http://{self.host}:{self.port}/sys/printer"
    
    def __str__(self):
        "Memobird string identification."""

        return f"Memobird at {self.host}:{self.port}"

    #TODO: Retroengineering of configuration packets
