# control/defaults.py
from control.panopticon import Panopticon
from control.capture.capture import Capture

DEFAULT_PANOPTICON = Panopticon(capture=Capture())
