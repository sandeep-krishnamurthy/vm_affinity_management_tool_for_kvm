#
# Copyright (C) 2013 IIIT-B
# Copyright (C) 2013 Sandeep Krishnamurthy <sandeep.k@iiitb.org> 
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

import logging

import gtk

from virtManager.baseclass import vmmGObjectUI

class vmaffinityAbout(vmmGObjectUI):
    def __init__(self):
        vmmGObjectUI.__init__(self, "vmaffinity-about.ui", "vmaffinity-about")
        self.window.connect_signals({
            "on_vmaffinity-about_delete_event": self.close,
            "on_vmaffinity-about_response": self.close,})

    def show(self):
        logging.debug("Showing vmaffinity about")
        self.topwin.present()

    def close(self, data1=None, data2=None):
        logging.debug("Closing vmaffinity about")
        self.topwin.hide()
        self.reset_state()
        return 1
    
    def reset_state(self):
    	vmmGObjectUI.__init__(self, "vmaffinity-about.ui", "vmaffinity-about")
        self.window.connect_signals({
            "on_vmaffinity-about_delete_event": self.close,
            "on_vmaffinity-about_response": self.close,})

    def _cleanup(self):
        pass

vmmGObjectUI.type_register(vmaffinityAbout)
        
    
