# -*- coding: utf-8 -*-

"""
All classes used to represent a Flex-LM config file
"""


class Server(object):
    """
    A class that hold a Server data
    """

    def __init__(self, *args, **kwargs):
        """Initialize a Server object.
        Form in the config file:
        SERVER host hostid [port] [PRIMARY_IS_MASTER] [HEARTBEAT_INTERVAL=seconds]
        No named parameters are of interest.

        """

        self.complete = False

        try:
            self.host = args[0]
            self.host_id = args[1]
        except:
            raise TypeError("Server line is missing a required parameter")

        self.port = None

        if len(args) >= 3:
            try:
                self.port = int(args[2])
            except:
                raise TypeError("Server port is not numeric")

        self.complete = True
