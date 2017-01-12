
try:
    isinstance("", basestring)

    def is_string(s):
        return isinstance(s, basestring)  # Python 3
except NameError:

    def is_string(s):
        return isinstance(s, str)  # Python 2
