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

class vmaffinityCreateNewRule(vmmGObjectUI):
    def __init__(self):
        vmmGObjectUI.__init__(self, "vmaffinity-createnewrule.ui", "vmaffinity-createnewrule")

        #Connect signals
        self.window.connect_signals({
            "addVMToAffinityGroupButton_clicked": self.addToGroupClicked,
            "removeVMFromAffinityGroupButton_clicked": self.removeFromGroupClicked,
            "cancelAffinityGroupCreation_clicked":self.cancel,
            "createAffinityGroupButton_clicked":self.createNewAffinityGroupClicked,
            "on_vmaffinitycreaterulewindow_delete_event": self.close,})
        
        #Initialize banner
        self.initbanner()
    
    def initbanner(self):
         self.bannerImageObject = self.window.get_object("vma-createnewrule-banner")
         self.bannerImageObject.set_from_file("/usr/local/share/virt-manager/icons/hicolor/16x16/actions/vmaffinitycreaterule.png")
         
    def show(self, parent):
        logging.debug("Showing vmaffinity create new affinity rule window")       
        self.topwin.set_transient_for(parent)
        self.topwin.present()

    def close(self):
        logging.debug("Closing vmaffinity create new affinity rule window")
        self.topwin.hide()
        return 1
        
    def cancel(self, ignore1=None, ignore2=None):
        logging.debug("Cancelling creation of new affinity rule")
        self.close()
        return 1
        
    def _cleanup(self):
        pass
    
    def addToGroupClicked():
        a=1+2
    
    def removeFromGroupClicked():
        a=1+2
    
    def cancelGroupCreation():
        a=1+2
    
    def createNewAffinityGroupClicked():
        a=1+2

vmmGObjectUI.type_register(vmaffinityCreateNewRule)
    
