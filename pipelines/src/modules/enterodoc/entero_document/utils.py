"""
Shared utility functions and data
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"


import signal


class dotdict(dict):
    """Enables dot.notation access to dictionary attributes
    ref: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    TODO: not picklable - use DotMap instead
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class timeout:
  """Timeout function after duration of seconds
  
  This uses `signal` and so is only useable on linux.
  
  Usage:
  with timeout(seconds=3):
    time.sleep(4)
  """
  def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
  def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
  def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
  def __exit__(self, type, value, traceback):
        signal.alarm(0)


def load_svg(filepath):
     """Load svg image from filepath."""
     image = ''
     with open(filepath, 'r') as f:
          image = f.read()
     return image


def get_clean_text(txt):
    """Get clean text for record['clean_body'] from record['body']."""
    if type(txt) is list:
        combined_txt = ('.').join(txt)
        return combined_txt.replace('.','.  ').replace('\n',' ')
    elif type(txt) is str:
        txts = txt.split('.\n')
        #TODO:if the len(item)<50, then append to the earlier item
        txts = [txt.replace('-\n','').replace('\n',' ') for txt in txts]
        txts = ' '.join(txts)
        return txts
    else:
        return txt
    

def bytes_to_megabytes(bytes_value):
    """Converts bytes to megabytes"""
    return bytes_value / (1024 * 1024)