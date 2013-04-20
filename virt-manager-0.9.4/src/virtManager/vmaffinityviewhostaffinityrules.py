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
import libvirt

from virtManager.baseclass import vmmGObjectUI
from virtManager import vmaffinityxmlutil
from virtManager.vmaffinityxmlutil import GroupDetails
from virtManager.vmaffinityxmlutil import HostAffinityDetails

class vmaffinityViewHostAffinityRules(vmmGObjectUI):
    
    # Initialization Code
    def __init__(self):
        
        # check if groups config file exists
        vmaffinityxmlutil.checkIfGroupsConfigExists()

        #initialize all UI components to none
        self.viewHostAffinityRulesImageBanner = None
        self.availableVirtualMachinesScrolledwindow = None
        self.selectedVMDesTextview = None
        self.selectedVMAffinedHostsScrolledwindow = None
        self.cancelViewHostAffinityRuleButton = None
        self.okViewHostAffinityRuleButton = None
        
        self.allVMsClist = None
        self.affinedHostsClist = None
        
        #CList related variables
        self.selectedVMRow = None
        self.selectedVMColumn = None
        
        self.allVMHostAffinityDictionary = None
        
        #Initialize window
        vmmGObjectUI.__init__(self, "vmaffinity-view-hostaffinityrules.ui", "vmaffinity-view-hostaffinity-rules")
        
        #Connect signals
        self.window.connect_signals({ 
        	"on_vmaffinity-view-configured-rules_delete_event":self.close,
        	"on_cancelViewHostAffinityRuleButton_clicked":self.close,
        	"on_okViewHostAffinityRuleButton_clicked":self.close,
        })
        
        #Initialize UI components
        self.initUIComponents()
        
        
    def initUIComponents(self):
        
        self.viewHostAffinityRulesImageBanner = self.widget("viewHostAffinityRulesImageBanner")
        self.availableVirtualMachinesScrolledwindow = self.widget("availableVirtualMachinesScrolledwindow")
        self.selectedVMDesTextview = self.widget("selectedVMDesTextview")
        self.selectedVMAffinedHostsScrolledwindow = self.widget("selectedVMAffinedHostsScrolledwindow")
        self.cancelViewHostAffinityRuleButton = self.widget("cancelViewHostAffinityRuleButton")
        self.okViewHostAffinityRuleButton = self.widget("okViewHostAffinityRuleButton")
        
        #Create List Objects
        self.allVMsClist = gtk.CList(1, "allVMsClist")
        self.affinedHostsClist = gtk.CList(1, "affinedHostsClist")
        
        self.allVMsClist.set_shadow_type(gtk.SHADOW_OUT)
        self.allVMsClist.column_titles_hide()
        self.allVMsClist.set_column_width(0, 150)
        self.allVMsClist.connect("select_row", self.allVMsClist_row_selected)
        self.allVMsClist.show()        
        self.availableVirtualMachinesScrolledwindow.add(self.allVMsClist)
        
        self.affinedHostsClist.set_shadow_type(gtk.SHADOW_OUT)
        self.affinedHostsClist.column_titles_hide()
        self.affinedHostsClist.set_column_width(0, 150)
        self.affinedHostsClist.connect("select_row", self.affinedHostsClist_row_selected)
        self.affinedHostsClist.show()
        self.selectedVMAffinedHostsScrolledwindow.add(self.affinedHostsClist)
        
        #initialize all the UI Components.
        self.init_banner()
        self.init_allVMsClist()
        self.init_affinedHostsClist()

        
    def init_banner(self):	
        self.viewHostAffinityRulesImageBanner.set_from_file("/usr/local/share/virt-manager/icons/hicolor/16x16/actions/vmaffinityviewhostaffinityrules.png")
    
    
    def init_allVMsClist(self):
        #TODO: Sandeep - Call dictionary method here, initialize dictionary object and append all groups c list.
        # Dictionary Structure: key = vm name, value = custom object(description, list of hosts).
        # Use reference of previously built GroupDetails class and getAffinityGroupDetails() methods in xmlutil code.
        # NoTE: If a VM does not have host affinity, keep description as empty and list as empty list.

        self.allVMsClist.clear()
        allVMsList = []
        
        # List all inactive domains:        
        connection = libvirt.open('qemu:///system')
        tempClist = connection.listDefinedDomains()
        for name in tempClist:
            self.allVMsClist.append([name])
            allVMsList.append(name)
        
        #List all active domains:
        tempList = connection.listDomainsID()
        for id in tempList:
        	dom = connection.lookupByID(id)
        	self.allVMsClist.append([dom.name()])
        	allVMsList.append(dom.name())
        
        # get Dictionary of defined host affinities.
        self.allVMHostAffinityDictionary = vmaffinityxmlutil.getHostAffinityDetailsDictionary(allVMsList)
        
        self.allVMsClist.select_row(0,0)
        return
        
    def init_affinedHostsClist(self):
        #TODO: Sandeep - Initially set first dictionary entry, vmlist and description.
        # Get dictionary and set the values of descriptions and affined host lists appropriately.
        # Handle empty list appropriately
        self.affinedHostsClist.clear()
            
        selectedGroupName = self.allVMsClist.get_text(0,0)

        if(selectedGroupName == None):
            return
        
        # Get group details object.
        selectedGroupDetails = self.allVMHostAffinityDictionary[selectedGroupName]
        
        # get description
        desc = ""
        if selectedGroupDetails.getDescription() != None:
        	desc = selectedGroupDetails.getDescription()
        	
        self.selectedVMDesTextview.get_buffer().set_text(desc)
        
        # get list of virtual machines in the group
        affinedHosts = selectedGroupDetails.getHostList()
        
        for host in affinedHosts:
            self.affinedHostsClist.append([host])
    	
    	return
    	
    def close(self, src_ignore=None, src2_ignore=None):
        logging.debug("Closing vmaffinity view host affinity rules window")
        self.topwin.hide()
        
        self.reset_state()
        
        return 1
    
    def reset_state(self):
        
        # check if groups config file exists
        vmaffinityxmlutil.checkIfGroupsConfigExists()

        #initialize all UI components to none
        self.viewHostAffinityRulesImageBanner = None
        self.availableVirtualMachinesScrolledwindow = None
        self.selectedVMDesTextview = None
        self.selectedVMAffinedHostsScrolledwindow = None
        self.cancelViewHostAffinityRuleButton = None
        self.okViewHostAffinityRuleButton = None
        
        self.allVMsClist = None
        self.affinedHostsClist = None
        
        #CList related variables
        self.selectedVMRow = None
        self.selectedVMColumn = None
        
        self.allVMHostAffinityDictionary = None
        
        #Initialize window
        vmmGObjectUI.__init__(self, "vmaffinity-view-hostaffinityrules.ui", "vmaffinity-view-hostaffinity-rules")
        
        #Connect signals
        self.window.connect_signals({ 
        	"on_vmaffinity-view-configured-rules_delete_event":self.close,
        	"on_cancelViewHostAffinityRuleButton_clicked":self.close,
        	"on_okViewHostAffinityRuleButton_clicked":self.close,
        })
        
        #Initialize UI components
        self.initUIComponents()
        
    def show(self, parent):
        logging.debug("Showing vmaffinity view vm-host affinity rules window")      
        self.topwin.set_transient_for(parent)
        self.topwin.present()        
       
    def _cleanup(self):
        self.reset_state()
    
    def affinedHostsClist_row_selected(self, clist, row, column, event, data=None):
        pass

    def allVMsClist_row_selected(self, clist, row, column, event, data=None):
        self.selectedVMRow = row
        self.selectedVMColumn = column
        
        #TODO: Sandeep - Get key value, selected group name, fetch the value object
        # clear selectedVMs clist and append new list, clear text view and append new desc.
        
        # Clear current contents
        self.affinedHostsClist.clear()
        self.selectedVMDesTextview.get_buffer().set_text("")
        
        # Get group details object.
        selectedGroupName = self.allVMsClist.get_text(row,column)
        selectedGroupDetails = self.allVMHostAffinityDictionary[selectedGroupName]
        
        # get description
        desc = ""
        if selectedGroupDetails.getDescription() != None:
        	desc = selectedGroupDetails.getDescription()
        	
        self.selectedVMDesTextview.get_buffer().set_text(desc)
        
        # get list of virtual machines in the group
        affinedHosts = selectedGroupDetails.getHostList()
        
        for host in affinedHosts:
            self.affinedHostsClist.append([host])
        
        return
        
vmmGObjectUI.type_register(vmaffinityViewHostAffinityRules)        
