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
from virtManager.error import vmmErrorDialog
from virtManager.vmaffinityxmlutil import HostAffinityDetails

class vmaffinityDeleteHostAffinityRule(vmmGObjectUI):
    
    #initialization code
    def __init__(self):
        
        # check if groups config file exists
        vmaffinityxmlutil.checkIfGroupsConfigExists()
        
        #initialize all UI components to none
        self.vmaDeleteHostAffinityBanner = None
        self.allVMsScrolledwindow = None
        self.selectedVMAffinedHostsScrolledwindow = None
        self.selectedRuleDesTextview = None
        self.cancelRuleDeletionButton = None
        self.DeleteHostAffinityButton = None
        self.errorLabel = None
       
        self.allVmsClist = None
        self.affinedHostsClist = None       
        
        #CList related variables
        self.selectedVMRow = None
        self.selectedVMColumn = None
        
        self.allVMHostAffinityDictionary = None
        
        vmmGObjectUI.__init__(self, "vmaffinity-deletehostaffinityrule.ui", "vmaffinity-deletehostaffinityrule")

        #Connect signals
        self.window.connect_signals({
            "on_cancelRuleDeletionButton_clicked": self.close,
            "on_DeleteHostAffinityButton_clicked":self.DeleteHostAffinityRuleButtonClicked,
            "on_vmaffinity-deletehostaffinityrule_delete_event": self.close,})
        
        #Initialize all UI components
        self.initUIComponents()
        

        self.err = vmmErrorDialog()
        
    def reset_state(self):

        #initialize all UI components to none
        self.vmaDeleteHostAffinityBanner = None
        self.allVMsScrolledwindow = None
        self.selectedVMAffinedHostsScrolledwindow = None
        self.selectedRuleDesTextview = None
        self.cancelRuleDeletionButton = None
        self.DeleteHostAffinityButton = None
        self.errorLabel = None
       
        self.allVmsClist = None
        self.affinedHostsClist = None       
        
        #CList related variables
        self.selectedVMRow = None
        self.selectedVMColumn = None
        
        self.allVMHostAffinityDictionary = None
        
        vmmGObjectUI.__init__(self, "vmaffinity-deleterule.ui", "vmaffinity-deleterule")

        #Connect signals
        self.window.connect_signals({
            "on_cancelRuleDeletionButton_clicked": self.close,
            "on_DeleteHostAffinityButton_clicked":self.DeleteHostAffinityRuleButtonClicked,
            "on_vmaffinity-deletehostaffinityrule_delete_event": self.close,})
        
        #Initialize all UI components
        self.initUIComponents()        

        self.err = vmmErrorDialog()
       
    def initUIComponents(self):
        
        self.vmaDeleteHostAffinityBanner = self.widget("vmaDeleteHostAffinityBanner")
        self.allVMsScrolledwindow = self.widget("allVMsScrolledwindow")
        self.selectedVMAffinedHostsScrolledwindow = self.widget("selectedVMAffinedHostsScrolledwindow")
        self.selectedRuleDesTextview = self.widget("selectedRuleDesTextview")
        self.cancelRuleDeletionButton = self.widget("cancelRuleDeletionButton")
        self.DeleteHostAffinityButton = self.widget("DeleteHostAffinityButton")
        self.errorLabel = self.widget("errorLabel")
        
        #Create List Objects
        self.allVmsClist = gtk.CList(1, "allVmsClist")
        self.affinedHostsClist = gtk.CList(1, "affinedHostsClist")
        
        self.allVmsClist.set_shadow_type(gtk.SHADOW_OUT)
        self.allVmsClist.column_titles_hide()
        self.allVmsClist.set_column_width(0, 150)
        self.allVmsClist.connect("select_row", self.allVmsClist_row_selected)
        self.allVmsClist.show()        
        self.allVMsScrolledwindow.add(self.allVmsClist)
        
        self.affinedHostsClist.set_shadow_type(gtk.SHADOW_OUT)
        self.affinedHostsClist.column_titles_hide()
        self.affinedHostsClist.set_column_width(0, 150)
        
        self.affinedHostsClist.show()
        self.selectedVMAffinedHostsScrolledwindow.add(self.affinedHostsClist)
        
        #initialize all the UI Components.
        self.init_banner()
        self.init_allVmsClist()
        self.init_affinedHostsClist()
        self.init_errorMessage()
        
                
    def init_banner(self):
        self.vmaDeleteHostAffinityBanner.set_from_file("/usr/local/share/virt-manager/icons/hicolor/16x16/actions/vmaffinitydeletehostaffinityrule.png")
    
    def init_allVmsClist(self):
        
        self.allVmsClist.clear()
        allVMsList = []
        
        # List all inactive domains:        
        connection = libvirt.open('qemu:///system')
        tempClist = connection.listDefinedDomains()
        for name in tempClist:
            self.allVmsClist.append([name])
            allVMsList.append(name)
        
        #List all active domains:
        tempList = connection.listDomainsID()
        for id in tempList:
        	dom = connection.lookupByID(id)
        	self.allVmsClist.append([dom.name()])
        	allVMsList.append(dom.name())
        
        # get Dictionary of defined host affinities.
        self.allVMHostAffinityDictionary = vmaffinityxmlutil.getHostAffinityDetailsDictionary(allVMsList)
        
        self.allVmsClist.select_row(0,0)
        return
		
        
    def init_affinedHostsClist(self):
        
       self.affinedHostsClist.clear()
            
       selectedGroupName = self.allVmsClist.get_text(0,0)

       if(selectedGroupName == None):
           return
        
       # Get group details object.
       selectedGroupDetails = self.allVMHostAffinityDictionary[selectedGroupName]
        
       # get description
       desc = ""
       if selectedGroupDetails.getDescription() != None:
           desc = selectedGroupDetails.getDescription()
        	
       self.selectedRuleDesTextview.get_buffer().set_text(desc)
        
       # get list of virtual machines in the group
       affinedHosts = selectedGroupDetails.getHostList()
        
       for host in affinedHosts:
           self.affinedHostsClist.append([host])
    	
       return
        
    def init_errorMessage(self):
        #Initially error message should be empty and error label should be invisible.
        self.errorLabel.set_text("")
        self.errorLabel.hide()
    
    def allVmsClist_row_selected(self, clist, row, column, event, data=None):
		
		self.selectedVMRow = row
		self.selectedVMColumn = column
        
        # Clear current contents
		self.affinedHostsClist.clear()
		self.selectedRuleDesTextview.get_buffer().set_text("")
        # Get group details object.
		selectedGroupName = self.allVmsClist.get_text(row,column)
		selectedGroupDetails = self.allVMHostAffinityDictionary[selectedGroupName]
		
        # get description
		desc = ""
		if selectedGroupDetails.getDescription() != None:
			desc = selectedGroupDetails.getDescription()
		
        # get list of virtual machines in the group
		self.selectedRuleDesTextview.get_buffer().set_text(desc)
		
		affinedHosts = selectedGroupDetails.getHostList()
		for host in affinedHosts:
			self.affinedHostsClist.append([host])
		
		return
           
    #Event Handlers
    
    def DeleteHostAffinityRuleButtonClicked(self, data=None):
      
        # Get selected VM name.
        selectedVMName = self.allVmsClist.get_text(self.selectedVMRow,self.selectedVMColumn)

        try:
        	# Get Host Affinity details of selected VM
        	selectedVMHostAffinityDetails = self.allVMHostAffinityDictionary[selectedVMName]
        	affinedHosts = selectedVMHostAffinityDetails.getHostList()
        	if (len(affinedHosts)==0):
        		self.err.show_info(_("%s is not affined to any hosts !!!") % str(selectedVMName), "", "Nothing To Delete", False)
        		return
        	
        	vmaffinityxmlutil.removeHostAffinityFromGroupConfig(selectedVMName)
        	vmaffinityxmlutil.removeHostAffinityFromVMConfig(selectedVMName)        
        except Exception, e:
            self.err.show_err(_("Error deleting VM-Host Affinity Rule: %s") % str(e))
            return
                            
        # show success pop-up.
        self.err.show_info(_("All Host Affinities of %s Successfully Deleted !!!") % str(selectedVMName), "", "Rule Deletion Success", False)
        
        # close window.
        self.close(None, None)    
        
        return
        
    def show(self, parent):
        logging.debug("Showing vmaffinity delete VM-Host affinity rule window")       
        self.topwin.set_transient_for(parent)
        self.topwin.present()


    def close(self, src_ignore=None, src2_ignore=None):
        
        logging.debug("Closing vmaffinity delete VM-Host affinity rule window")
        self.topwin.hide()
        
        self.reset_state()
 
        return 1
               
    def _cleanup(self):
        self.reset_state()
    
    def show_error_message(self, data):
        
        self.errorLabel.set_visible(True)
        self.errorLabel.set_text(data)       
    
    def hide_error_message(self):
        self.errorLabel.set_text("")
        self.errorLabel.set_visible(False)
  
vmmGObjectUI.type_register(vmaffinityDeleteHostAffinityRule)
