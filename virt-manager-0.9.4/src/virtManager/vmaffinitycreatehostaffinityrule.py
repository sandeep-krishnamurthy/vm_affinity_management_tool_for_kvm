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
import libvirt
import gtk

import socket
from virtManager.baseclass import vmmGObjectUI
from virtManager import vmaffinityxmlutil
from virtManager.error import vmmErrorDialog

class vmaffinityCreateHostAffinityRule(vmmGObjectUI):
    
    # Initialization Code
    def __init__(self):
        
        # check if groups config file exists
        vmaffinityxmlutil.checkIfGroupsConfigExists()
        
        #initialize all UI components to none
        self.affinedHostsTextEntry = None
        self.newRuleDescriptionTextView = None
        self.availableVirtualMachineScrolledwindow = None
        self.addVMToAffinityGroupbutton = None
        self.removeVMFromAffinityGroup = None
        self.affinedVirtualMachineScrolledwindow = None
        self.cancelHostAffinityRuleCreationButton = None
        self.CreateHostAffinityRuleButton = None
        self.warningLabel = None
        self.vmacreatehostaffinityrulebanner = None
        
        self.allVMClist = None
        self.affinedVMClist = None
                
        #CList related variables
        self.selectedAllVMRow = None
        self.selectedAllVMColumn = None
        self.selectedAffinedVMRow = None
        self.selectedAffinedVMColumn = None
        
        self.totalVMsAffined = 0
                
        vmmGObjectUI.__init__(self, "vmaffinity-createhostaffinityrule.ui", "vmaffinity-createhostaffinityrule")

        #Connect signals
        self.window.connect_signals({
            "on_addVMToAffinityGroupbutton_clicked": self.addVMToGroupClicked,
            "on_removeVMFromAffinityGroup_clicked": self.removeVMFromGroupClicked,
            "on_cancelHostAffinityRuleCreationButton_clicked":self.close,
            "on_CreateHostAffinityRuleButton_clicked":self.createNewHostAffinityRuleClicked,
            "on_vmaffinity-createhostaffinityrule_delete_event": self.close,
            })
        
        #Initialize UI components
        self.initUIComponents()
        
    def initUIComponents(self):
    	
    	self.affinedHostsTextEntry = self.widget("affinedHostsTextEntry")
        self.newRuleDescriptionTextView = self.widget("newRuleDescriptionTextView")
        self.availableVirtualMachineScrolledwindow = self.widget("availableVirtualMachineScrolledwindow")
        self.addVMToAffinityGroupbutton = self.widget("addVMToAffinityGroupbutton")
        self.removeVMFromAffinityGroup = self.widget("removeVMFromAffinityGroup")
        self.affinedVirtualMachineScrolledwindow = self.widget("affinedVirtualMachineScrolledwindow")
        self.cancelHostAffinityRuleCreationButton = self.widget("cancelHostAffinityRuleCreationButton")
        self.CreateHostAffinityRuleButton = self.widget("CreateHostAffinityRuleButton")
        self.warningLabel = self.widget("warningLabel")
        self.vmacreatehostaffinityrulebanner = self.widget("vmacreatehostaffinityrulebanner")
        
        #create all virtual machine CList and vms in new group list.
        
        self.allVMClist = gtk.CList(1, "allVMClist")
        self.affinedVMClist = gtk.CList(1, "affinedVMClist")
        
        self.allVMClist.set_shadow_type(gtk.SHADOW_OUT)
        self.allVMClist.column_titles_hide()
        self.allVMClist.set_column_width(0, 150)
        self.allVMClist.connect("select_row", self.allVMClist_row_selected)
        self.allVMClist.show()        
        self.availableVirtualMachineScrolledwindow.add(self.allVMClist)
        
        self.affinedVMClist.set_shadow_type(gtk.SHADOW_OUT)
        self.affinedVMClist.column_titles_hide()
        self.affinedVMClist.set_column_width(0, 150)
        self.affinedVMClist.connect("select_row", self.affinedVMClist_row_selected)
        self.affinedVMClist.show()
        self.affinedVirtualMachineScrolledwindow.add(self.affinedVMClist)
        
        self.err = vmmErrorDialog()
        #initialize all the UI Components.
        self.init_banner()
        self.init_allVMList()
        self.init_affinedVMList()
        self.init_errorMessage()
    
    def init_banner(self):
        self.vmacreatehostaffinityrulebanner.set_from_file("/usr/local/share/virt-manager/icons/hicolor/16x16/actions/vmaffinitycreatehostaffinityrule.png")
    
    def init_allVMList(self):
       
        self.allVMClist.clear()
        
        # List all inactive domains:        
        connection = libvirt.open('qemu:///system')
        self.allVMList = connection.listDefinedDomains()
        for name in self.allVMList:
            self.allVMClist.append([name])
        
        #List all active domains:
        tempList = connection.listDomainsID()
        for id in tempList:
        	dom = connection.lookupByID(id)
        	self.allVMClist.append([dom.name()])
        
        #default selection
        self.allVMClist.select_row(0,0)
        
        return
        
    def init_affinedVMList(self):
		#Initially this list should be empty.
        self.affinedVMClist.clear()
        return
        
    def init_errorMessage(self):
        #Initially error message should be empty and error label should be invisible.
        self.warningLabel.set_text("")
        self.warningLabel.hide()
    
    # Event Handlers
    
    def addVMToGroupClicked(self, data=None):

        selectedVM = self.allVMClist.get_text(self.selectedAllVMRow, self.selectedAllVMColumn)
        
        self.allVMClist.freeze()
        
        self.allVMClist.remove(self.selectedAllVMRow)
        
        self.allVMClist.thaw()
        
        #self.warningLabel.set_text("Add event handler, row = %d, selected VM = %s\n " %(self.selectedAllVMRow, selectedVM))
       
        self.affinedVMClist.append([selectedVM])
        
        self.totalVMsAffined = self.totalVMsAffined + 1
        
        self.affinedVMClist.select_row(0,0)
        self.allVMClist.select_row(0,0)  
        return
        
    def removeVMFromGroupClicked(self, data=None):

        selectedVM = self.affinedVMClist.get_text(self.selectedAffinedVMRow, self.selectedAffinedVMColumn)
        
        self.affinedVMClist.freeze()
        
        self.affinedVMClist.remove(self.selectedAffinedVMRow)
        
        self.affinedVMClist.thaw()
        
        #self.warningLabel.set_text("Remove event handler, row = %d, selected VM = %s\n " %(self.selectedAffinedVMRow, selectedVM))
       
        self.allVMClist.append([selectedVM])

        self.totalVMsAffined = self.totalVMsAffined - 1
        if self.totalVMsAffined < 0:
            self.totalVMsAffined = 0
        
        self.allVMClist.select_row(0,0)
        self.affinedVMClist.select_row(0,0)
        return
    
    def getListFromString(self, inString):
    	myList = []
    	newList = []
    	myList = inString.split(",")
    	return myList
    	#for i in range(len(myList)):
    	#	x = myList[i]
    	#	self.err.show_err(_("String: %s") % str(x))
    	#	newList.append(x.strip())
		#return newList

	
    def createNewHostAffinityRuleClicked(self, data=None):
		
    	# 1. Fetch comma separated host names.
    	self.affinedHostList = self.affinedHostsTextEntry.get_text()

        # check if empty
        if self.affinedHostList == None or self.affinedHostList == "":
        	self.show_error_message("ERROR: Affined Host Text Entry cannot be empty.")
        	return
        
        # Split by comma and form list, It should have entry only localhost or a valid IP address.
        #TODO: Sandeep, do above tasks
        hostList = self.getListFromString(self.affinedHostList)
        try:
        	for addr in hostList:
        	    if addr == "localhost":
        	    	a = 1
        	    else:
        	    	tempAddr = addr
        	    	socket.inet_aton(tempAddr)
        except Exception, e:
			self.show_error_message("ERROR: Invalid affined hosts IP Address.")
			return
            
            
        # get description
        text_buffer = self.newRuleDescriptionTextView.get_buffer()
        self.newGroupDescription = ""
        if text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter(), True) != None:
        	self.newGroupDescription = text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter(), True)
        
        # VMList count validation (Minimum 1 vm must be selected)
        if self.totalVMsAffined <= 0:
            self.show_error_message("ERROR: Atleast 1 virtual machines should be selected in a VM-Host Affinity Rule.")
            return
            
        # Create rule
        self.hide_error_message()
        
       	# For Each vm selected update groups config and individual vm config file with host affinity details.
        try:
		
            for i in range(self.totalVMsAffined):
            	tempVM = self.affinedVMClist.get_text(i, 0)
            	vmaffinityxmlutil.updateGroupConfigForHostAffinity(tempVM,self.newGroupDescription, hostList)
            	vmaffinityxmlutil.updateVMConfigForHostAffinity(tempVM, self.newGroupDescription, hostList)
        except Exception, e:
        	self.err.show_err(_("Error creating Affinity Rule: %s") % str(e))
        	return
                            
        # show success pop-up.
        self.err.show_info(_("VM-Host Affinity Rule Successfully Created !!!"), "", "Rule Creation Success", False)
        
        # close window.
        self.close(None, None)       
        
    
    # Helper Methods:
	
    def close(self, src_ignore=None, src2_ignore=None):
        logging.debug("Closing vmaffinity create new VM-Host affinity rule window")
        self.topwin.hide()
        
        self.reset_state()
		
        return 1
    
    def reset_state(self):
    	#initialize all UI components to none
        self.affinedHostsTextEntry = None
        self.newRuleDescriptionTextView = None
        self.availableVirtualMachineScrolledwindow = None
        self.addVMToAffinityGroupbutton = None
        self.removeVMFromAffinityGroup = None
        self.affinedVirtualMachineScrolledwindow = None
        self.cancelHostAffinityRuleCreationButton = None
        self.CreateHostAffinityRuleButton = None
        self.warningLabel = None
        self.vmacreatehostaffinityrulebanner = None
        
        self.allVMClist = None
        self.affinedVMClist = None
                
        #CList related variables
        self.selectedAllVMRow = None
        self.selectedAllVMColumn = None
        self.selectedAffinedVMRow = None
        self.selectedAffinedColumn = None
        
        self.totalVMsAffined = 0
                
        vmmGObjectUI.__init__(self, "vmaffinity-createhostaffinityrule.ui", "vmaffinity-createhostaffinityrule")

        #Connect signals
        self.window.connect_signals({
            "on_addVMToAffinityGroupbutton_clicked": self.addVMToGroupClicked,
            "on_removeVMFromAffinityGroup_clicked": self.removeVMFromGroupClicked,
            "on_cancelHostAffinityRuleCreationButton_clicked":self.close,
            "on_CreateHostAffinityRuleButton_clicked":self.createNewHostAffinityRuleClicked,
            "on_vmaffinity-createhostaffinityrule_delete_event": self.close,
            })
        
        #Initialize UI components
        self.initUIComponents()
    
    def show(self, parent):
        logging.debug("Showing vmaffinity create new VM-Host affinity rule window.")       
        self.topwin.set_transient_for(parent)
        self.topwin.present()


    def _cleanup(self):        
        self.reset_state() 
    
    def allVMClist_row_selected(self, clist, row, column, event, data=None):
        self.selectedAllVMRow = row
        self.selectedAllVMColumn = column
        self.show_error_message()

    def affinedVMClist_row_selected(self, clist, row, column, event, data=None):
        self.selectedAffinedVMRow = row
        self.selectedAffinedVMColumn = column

    def show_error_message(self, data):
        
        self.warningLabel.set_visible(True)
        self.warningLabel.set_text(data)
        #self.warningLabel.set_text("you selected : " + str(self.selectedAffinedVMRow) + str(self.selectedAffinedColumn))
    
    def hide_error_message(self):
    
        self.warningLabel.set_text("")
        self.warningLabel.set_visible(False)

vmmGObjectUI.type_register(vmaffinityCreateHostAffinityRule)
