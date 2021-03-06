# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2015-2016 Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import ctypes
import ctypes.util
import array
from .errors import DiscordException
import logging

log = logging.getLogger(__name__)
c_int_ptr = ctypes.POINTER(ctypes.c_int)
c_int16_ptr = ctypes.POINTER(ctypes.c_int16)
c_float_ptr = ctypes.POINTER(ctypes.c_float)

class EncoderStruct(ctypes.Structure):
    pass

EncoderStructPtr = ctypes.POINTER(EncoderStruct)

# A list of exported functions.
# The first argument is obviously the name.
# The second one are the types of arguments it takes.
# The third is the result type.
exported_functions = [
    ('opus_strerror', [ctypes.c_int], ctypes.c_char_p),
    ('opus_encoder_get_size', [ctypes.c_int], ctypes.c_int),
    ('opus_encoder_create', [ctypes.c_int, ctypes.c_int, ctypes.c_int, c_int_ptr], EncoderStructPtr),
    ('opus_encode', [EncoderStructPtr, c_int16_ptr, ctypes.c_int, ctypes.c_char_p, ctypes.c_int32], ctypes.c_int32),
    ('opus_encoder_destroy', [EncoderStructPtr], None)
]

def libopus_loader(name):
    # create the library...
    lib = ctypes.cdll.LoadLibrary(name)

    # register the functions...
    for item in exported_functions:
        try:
            func = getattr(lib, item[0])
        except Exception as e:
            raise e

        try:
            func.argtypes = item[1]
            func.restype = item[2]
        except KeyError:
            pass

    return lib

try:
    _lib = libopus_loader(ctypes.util.find_library('opus'))
except:
    _lib = None

def load_opus(name):
    """Loads the libopus shared library for use with voice.

    If this function is not called then the library uses the function
    `ctypes.util.find_library`__ and then loads that one
    if available.

    .. _find library: https://docs.python.org/3.5/library/ctypes.html#finding-shared-libraries
    __ `find library`_

    Not loading a library leads to voice not working.

    This function propagates the exceptions thrown.

    Warning
    --------
    The bitness of the library must match the bitness of your python
    interpreter. If the library is 64-bit then your python interpreter
    must be 64-bit as well. Usually if there's a mismatch in bitness then
    the load will throw an exception.

    Note
    ----
    On Windows, the .dll extension is not necessary. However, on Linux
    the full extension is required to load the library, e.g. ``libopus.so.1``.
    On Linux however, `find library`_ will usually find the library automatically
    without you having to call this.

    Parameters
    ----------
    name: str
        The filename of the shared library.
    """
    global _lib
    _lib = libopus_loader(name)

def is_loaded():
    """Function to check if opus lib is successfully loaded either
    via the ``ctypes.util.find_library`` call of :func:`load_opus`.

    This must return ``True`` for voice to work.

    Returns
    -------
    bool
        Indicates if the opus library has been loaded.
    """
    global _lib
    return _lib is not None

class OpusError(DiscordException):
    """An exception that is thrown for libopus related errors.

    Attributes
    ----------
    code : int
        The error code returned.
    """
    def __init__(self, code):
        self.code = code
        msg = _lib.opus_strerror(self.code).decode('utf-8')
        log.info('"{}" has happened'.format(msg))
        super().__init__(msg)

class OpusNotLoaded(DiscordException):
    """An exception that is thrown for when libopus is not loaded."""
    pass


# Some constants...
OK = 0
APPLICATION_AUDIO    = 2049
APPLICATION_VOIP     = 2048
APPLICATION_LOWDELAY = 2051

class Encoder:
    def __init__(self, sampling, channels, application=APPLICATION_AUDIO):
        self.sampling_rate = sampling
        self.channels = channels
        self.application = application

        self.frame_length = 20
        self.sample_size = 2 * self.channels # (bit_rate / 8) but bit_rate == 16
        self.samples_per_frame = int(self.sampling_rate / 1000 * self.frame_length)
        self.frame_size = self.samples_per_frame * self.sample_size

        if not is_loaded():
            raise OpusNotLoaded()

        self._state = self._create_state()

    def __del__(self):
        if hasattr(self, '_state'):
            _lib.opus_encoder_destroy(self._state)
            self._state = None

    def _create_state(self):
        ret = ctypes.c_int()
        result = _lib.opus_encoder_create(self.sampling_rate, self.channels, self.application, ctypes.byref(ret))

        if ret.value != 0:
            log.info('error has happened in state creation')
            raise OpusError(ret.value)

        return result

    def encode(self, pcm, frame_size):
        max_data_bytes = len(pcm)
        pcm = ctypes.cast(pcm, c_int16_ptr)
        data = (ctypes.c_char * max_data_bytes)()

        ret = _lib.opus_encode(self._state, pcm, frame_size, data, max_data_bytes)
        if ret < 0:
            log.info('error has happened in encode')
            raise OpusError(ret)

        return array.array('b', data[:ret]).tobytes()
