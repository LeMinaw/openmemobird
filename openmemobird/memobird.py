from base64 import b64encode
from random import randint
from PIL import Image as PILImg, ImageOps
from io import BytesIO
import requests


def to_byte_array(img):
    imgByteArr = BytesIO()
    img.save(imgByteArr, format='bmp')
    return imgByteArr.getvalue()


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


class Document:
    
    def __init__(self, print_id=None):
        """Creates a document for print. print_id can be specified if needed, otherwise a
        dummy print id will be generated."""
        
        self.print_id = print_id or randint(1, 10**6)
        self.elems = []

    def add(self, elem):
        """Adds an element to the document."""

        self.elems.append(elem)
    
    def get_orders(self):
        """Returns the print orders for the whole document."""

        return {
            'command': 3,
            'content': {
                'textList': [elem.get_orders() for elem in self.elems]
            },
            'encryptFlag': 0,
            'hasHead': 0,
            'hasSignature': 0,
            'hasTail': 0,
            'isFromDirectPrint': False,
            'msgType': 1,
            'pkgCount': 1,
            'pkgNo': 1,
            'printID': self.print_id,
            'priority': 0,
            'result': 0,
            'scripType': 3
        }
    
    def print(self, memobird):
        """Sends the document to the memobird for printing. Proper connection must be
        provided!"""

        rqst = requests.post(memobird.uri, verify=False, json=self.get_orders())
        if rqst.status_code == 500:
            raise RuntimeError("Memobird returned error code 500. Print job aborted.")
        return rqst.status_code

    def show(self):
        """Helper function to preview document in text mode."""
        
        for elem in self.elems:
            print(elem)



class Element:
    
    def get_orders(self):
        """Returns the print orders for this element."""

        return {'encodeType': 0}


class Image(Element):

    def __init__(self, path):
        """Creates an image. path must be a valid path to an image.
        Non-monochrome images will be automatically converted. Max
        width is 384px. Warning: images exceding a given size limit
        will make memobird throw 500."""

        self.img_path = path #TODO: Validate image filesize and dimensions
    
    def get_orders(self):
        """Returns the orders print orders for this element."""

        orders = super().get_orders()
        orders['printType'] = 5
        img = PILImg.open(self.img_path)
        img = img.convert(mode='L') # Ensure ImageOps will handle the data
        # img = ImageOps.invert(img) # Was needed before BMP header support
        img = ImageOps.mirror(img) # Fixes BMP format columns order
        img = img.convert(mode='1') # Memobird needs 1-bit monochrome
        orders['basetext'] = b64encode(to_byte_array(img)).decode()
        return orders
    
    def __str__(self):
        """String preview of this element."""

        return f"[[ IMAGE {self.img_path} ]]"


class Sticker(Element):

    def __init__(self, sticker_id):
        """Creates a sticker. sticker_id is an int identifying the sticker."""

        self.sticker_id = sticker_id
    
    def get_orders(self):
        """Returns the print orders for this element."""
        
        orders = super().get_orders()
        orders['printType'] = 4
        orders['iconID'] = self.sticker_id
        return orders
    
    def __str__(self):
        """String preview of this element."""

        return f"[[ STICKER {self.sticker_id} ]]"


class Line(Sticker):

    def __init__(self, linetype='THICK'):
        """Creates an horizontal line. linetype can be 'THICK', 'THIN', or 'DASH'.""" 

        self.linetype = linetype
        lines_codes = {
            'THICK': 41,
            'THIN': 42,
            'DASH': 43
        }
        super().__init__(lines_codes[linetype])
    
    def __str__(self):
        """String preview of this element."""

        if self.linetype == 'THICK':
            return '=' * 25
        if self.linetype == 'DASH':
            return '= ' * 12 + '='
        return '-' * 25
        


class Text(Element):
    
    def __init__(self, text, big=False, bold=False, underline=False):
        """Creates a paragraph of text. big, bold and underline styles can be applied."""

        self.text      = text
        self.big       = big
        self.bold      = bold
        self.underline = underline
    
    def get_orders(self):
        """Returns the print orders for this element."""

        text = self.text
        if not text.endswith('\n'):
            text += '\n'
        orders = super().get_orders()
        orders['printType'] = 1
        orders['basetext'] = b64encode(text.encode("GBK")).decode()
        orders['fontSize'] = 1 + self.big
        orders['bold'] = 1 * self.bold
        orders['underline'] = 1 * self.underline
        return orders
    
    def __str__(self):
        """String preview of this element."""

        txt = self.text
        if self.underline:
            txt = f"_{txt}_"
        if self.bold:
            txt = f"**{txt}**"
        if self.big:
            txt = f"# {txt} #"
        return txt