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

class vmaffinityManageRules(vmmGObjectUI):
    
    # Initialization Code
    def __init__(self):
        
        # check if groups config file exists
        vmaffinityxmlutil.checkIfGroupsConfigExists()

        #initialize all UI components to none        
        self.manageRuleBanner = None
        self.configuredAffinityRulesScrolledwindow = None
        self.selectedRuleDesTextview = None
        self.selectedAffinityRuleVMsScrolledwindow = None
        self.availableVirtualMachineScrolledwindow = None
        self.updatedGroupVirtualMachineScrolledwindow = None
        self.addVMToUpdatedAffinityGroupbutton = None
        self.removeVMFromUpdatedAffinityGroupButton = None
        self.cancelRuleManageButton = None
        self.UpdateAffinityGroupButton = None
        self.errorLabel = None
        
        self.allGroupsClist = None
        self.VMsInGroupClist = None          
        
        # CList for managing
        self.universalVMList = None
        self.VMsInUpdatedGroupClist = None
        
        # CList variables for managing
        self.universalSelectedVMRow = None
        self.universalSelectedVMColumn = None
        
        self.updatedListSelectedVMRow = None
        self.updatedListSelectedVMColumn = None
        
        #CList related variables
        self.selectedGroupRow = None
        self.selectedGroupColumn = None
        
        self.allGroupDictionary = None
        
        # List of all available machines in this machine
        self.allVMsInMachine = None
        
        vmmGObjectUI.__init__(self, "vmaffinity-manage-affinity-rules.ui", "vmaffinity-manage-affinity-rules")
        
        #Connect signals
        self.window.connect_signals({"on_addVMToUpdatedAffinityGroupbutton_clicked": self.addVMToUpdatedAffinityGroup,
        	"on_removeVMFromUpdatedAffinityGroupButton_clicked": self.removeVMFromUpdatedAffinityGroup,    				"on_cancelRuleManageButton_clicked": self.close, 
        	"on_UpdateAffinityGroupButton_clicked": self.UpdateAffinityGroup,
        	"on_vmaffinity-manage-affinity-rules_delete_event": self.close,
        })
        
        # a counter to keep track on how many virtual machines in updated group vm members.
        self.totalVMsInUpdatedGroup = 0
        
		#Initialize all UI components
        self.initUIComponents()
        
        self.err = vmmErrorDialog()
        
    def initUIComponents(self):
    
        self.manageRuleBanner = self.widget("manageRuleBanner")
        self.configuredAffinityRulesScrolledwindow = self.widget("configuredAffinityRulesScrolledwindow")
        self.selectedRuleDesTextview = self.widget("selectedRuleDesTextview")
        self.selectedAffinityRuleVMsScrolledwindow = self.widget("selectedAffinityRuleVMsScrolledwindow")
        self.availableVirtualMachineScrolledwindow = self.widget("availableVirtualMachineScrolledwindow")
        self.updatedGroupVirtualMachineScrolledwindow = self.widget("updatedGroupVirtualMachineScrolledwindow")
        self.addVMToUpdatedAffinityGroupbutton = self.widget("addVMToUpdatedAffinityGroupbutton")
        self.removeVMFromUpdatedAffinityGroupButton = self.widget("removeVMFromUpdatedAffinityGroupButton")
        self.cancelRuleManageButton = self.widget("cancelRuleManageButton")
        self.UpdateAffinityGroupButton = self.widget("UpdateAffinityGroupButton")
        self.errorLabel = self.widget("errorLabel")
        
        #Create List Objects
        self.allGroupsClist = gtk.CList(1, "allGroupsClist")
        self.VMsInGroupClist = gtk.CList(1, "VMsInGroupClist")
        
        self.allGroupsClist.set_shadow_type(gtk.SHADOW_OUT)
        self.allGroupsClist.column_titles_hide()
        self.allGroupsClist.set_column_width(0, 150)
        self.allGroupsClist.connect("select_row", self.allGroupsClist_row_selected)
        self.allGroupsClist.show()        
        self.configuredAffinityRulesScrolledwindow.add(self.allGroupsClist)
        
        self.VMsInGroupClist.set_shadow_type(gtk.SHADOW_OUT)
        self.VMsInGroupClist.column_titles_hide()
        self.VMsInGroupClist.set_column_width(0, 150)
        
        self.VMsInGroupClist.show()
        self.selectedAffinityRuleVMsScrolledwindow.add(self.VMsInGroupClist)
        
        #create List objects for managing
        
        # CList for managing
        self.universalVMList = gtk.CList(1, "universalVMList")
        self.VMsInUpdatedGroupClist = gtk.CList(1, "VMsInUpdatedGroupClist")
        
        self.universalVMList.set_shadow_type(gtk.SHADOW_OUT)
        self.universalVMList.column_titles_hide()
        self.universalVMList.set_column_width(0, 150)
        self.universalVMList.connect("select_row", self.universalVMList_row_selected)
        self.universalVMList.show()        
        self.availableVirtualMachineScrolledwindow.add(self.universalVMList)

        self.VMsInUpdatedGroupClist.set_shadow_type(gtk.SHADOW_OUT)
        self.VMsInUpdatedGroupClist.column_titles_hide()
        self.VMsInUpdatedGroupClist.set_column_width(0, 150)
        self.VMsInUpdatedGroupClist.connect("select_row", self.VMsInUpdatedGroupClist_row_selected)
        self.VMsInUpdatedGroupClist.show()        
        self.updatedGroupVirtualMachineScrolledwindow.add(self.VMsInUpdatedGroupClist)            
     
        #initialize all the UI Components.
        self.init_banner()
        self.init_allGroupsClist()
        self.init_VMsInGroupClist()
        
        # initialize manage related clists.
        #self.init_universalVMList()
        #self.init_VMsInUpdatedGroupClist()
        
        self.init_errorMessage()
        
    
    def init_banner(self):
        self.manageRuleBanner.set_from_file("/usr/local/share/virt-manager/icons/hicolor/16x16/actions/vmaffinitymanagerules.png")
        
    def init_allGroupsClist(self):
        #TODO: Sandeep - Call dictionary method here, initialize dictionary object and append all groups c list.
        
        self.allGroupsClist.clear()
        
        self.allGroupDictionary = vmaffinityxmlutil.getAffinityGroupDetails()
        countOfGroups = len(self.allGroupDictionary)
        if(countOfGroups == 0):
            return
        
        for group in self.allGroupDictionary.keys():
            self.allGroupsClist.append([group])
        
        # default selection.
        self.allGroupsClist.select_row(0,0)

        return
        
    def init_VMsInGroupClist(self):
        #TODO: Sandeep - Initially set first dictionary entry, vmlist and description.
        self.VMsInGroupClist.clear()
        
        # If count of groups itself is 0, there is nothing to do
        countOfGroups = len(self.allGroupDictionary)
        if(countOfGroups == 0):
            return
            
        selectedGroupName = self.allGroupsClist.get_text(0,0)

        if(selectedGroupName == None):
            return
        
        # Get group details object.
        selectedGroupDetails = self.allGroupDictionary[selectedGroupName]
        
        # get description
        
        self.selectedRuleDesTextview.get_buffer().set_text(selectedGroupDetails.getDescription())
        # get list of virtual machines in the group
        memberVMs = selectedGroupDetails.getVMList()
        
        for vm in memberVMs:
            self.VMsInGroupClist.append([vm])
        
        # Update Universal Clist
        self.update_universalVMList(memberVMs)
        
        # Update update VM Clist
        self.update_VMsInUpdatedGroupClist(memberVMs)
        return
    
    def init_universalVMList(self):
        
        pass
    
    def init_VMsInUpdatedGroupClist(self):
       
        return
    
    def init_errorMessage(self):
        #Initially error message should be empty and error label should be invisible.
        self.errorLabel.set_text("")
        self.errorLabel.hide()
    
    def allGroupsClist_row_selected(self, clist, row, column, event, data=None):
        self.selectedGroupRow = row
        self.selectedGroupColumn = column
        
        #TODO: Sandeep - Get key value, selected group name, fetch the value object
        # clear selectedVMs clist and append new list, clear text view and append new desc.
        
        # Clear current contents
        self.VMsInGroupClist.clear()
        self.selectedRuleDesTextview.get_buffer().set_text("")
        
        # Get group details object.
        selectedGroupName = self.allGroupsClist.get_text(row,column)
        selectedGroupDetails = self.allGroupDictionary[selectedGroupName]
        
        # Get Description        
        self.selectedRuleDesTextview.get_buffer().set_text(selectedGroupDetails.getDescription())
        
        # get list of virtual machines in the group
        memberVMs = selectedGroupDetails.getVMList()
        
        for vm in memberVMs:
            self.VMsInGroupClist.append([vm])
        
        # Update Universal Clist
        self.update_universalVMList(memberVMs)
        
        # Update update VM Clist
        self.update_VMsInUpdatedGroupClist(memberVMs)
        
        return
    
    def universalVMList_row_selected(self, clist, row, column, event, data=None):
        self.universalSelectedVMRow = row
        self.universalSelectedVMColumn = column
       
        return
    
    def VMsInUpdatedGroupClist_row_selected(self, clist, row, column, event, data=None):
        
        self.updatedListSelectedVMRow = row
        self.updatedListSelectedVMColumn = column
       
        return
    
    def show(self, parent):
        logging.debug("Showing vmaffinity manage affinity rule window")       
        self.topwin.set_transient_for(parent)
        self.topwin.present()


    def close(self, src_ignore=None, src2_ignore=None):
        logging.debug("Closing vmaffinity manage affinity rule window")
        self.topwin.hide()
        
        self.reset_state()
		
        return 1
        
    def reset_state(self):
    	
    	 #initialize all UI components to none        
        self.manageRuleBanner = None
        self.configuredAffinityRulesScrolledwindow = None
        self.selectedRuleDesTextview = None
        self.selectedAffinityRuleVMsScrolledwindow = None
        self.availableVirtualMachineScrolledwindow = None
        self.updatedGroupVirtualMachineScrolledwindow = None
        self.addVMToUpdatedAffinityGroupbutton = None
        self.removeVMFromUpdatedAffinityGroupButton = None
        self.cancelRuleManageButton = None
        self.UpdateAffinityGroupButton = None
        self.errorLabel = None
        
        self.allGroupsClist = None
        self.VMsInGroupClist = None          
        
        # CList for managing
        self.universalVMList = None
        self.VMsInUpdatedGroupClist = None
        
        # CList variables for managing
        self.universalSelectedVMRow = None
        self.universalSelectedVMColumn = None
        
        self.updatedListSelectedVMRow = None
        self.updatedListSelectedVMColumn = None
        
        #CList related variables
        self.selectedGroupRow = None
        self.selectedGroupColumn = None
        
        self.allGroupDictionary = None
        
        # List of all available machines in this machine
        self.allVMsInMachine = None
        
        vmmGObjectUI.__init__(self, "vmaffinity-manage-affinity-rules.ui", "vmaffinity-manage-affinity-rules")
        
        #Connect signals
        self.window.connect_signals({"on_addVMToUpdatedAffinityGroupbutton_clicked": self.addVMToUpdatedAffinityGroup,
        	"on_removeVMFromUpdatedAffinityGroupButton_clicked": self.removeVMFromUpdatedAffinityGroup,    				"on_cancelRuleManageButton_clicked": self.close, 
        	"on_UpdateAffinityGroupButton_clicked": self.UpdateAffinityGroup,
        	"on_vmaffinity-manage-affinity-rules_delete_event": self.close,
        })
        
        # a counter to keep track on how many virtual machines in updated group vm members.
        self.totalVMsInUpdatedGroup = 0
        
		#Initialize all UI components
        self.initUIComponents()
        
        self.err = vmmErrorDialog()
    	
    
    def _cleanup(self):

        self.reset_state() 
    
    def show_error_message(self, data):
        
        self.errorLabel.set_visible(True)
        self.errorLabel.set_text(data)       
    
    def hide_error_message(self):
        self.errorLabel.set_text("")
        self.errorLabel.set_visible(False)
    
    def addVMToUpdatedAffinityGroup(self, data=None):        
        # Move selected vm from universal list to updated vm group list
        
        selectedVM = self.universalVMList.get_text(self.universalSelectedVMRow, self.universalSelectedVMColumn)
        
        self.universalVMList.remove(self.universalSelectedVMRow)
        
        self.VMsInUpdatedGroupClist.append([selectedVM])
        
        self.totalVMsInUpdatedGroup = self.totalVMsInUpdatedGroup + 1
        
        self.VMsInUpdatedGroupClist.select_row(0,0)
        self.universalVMList.select_row(0,0)  
        
        return
    
    def removeVMFromUpdatedAffinityGroup(self, data=None):        
        # Move selected vm from updatedVMGroupList to UniversalList.
       
	    selectedVM = self.VMsInUpdatedGroupClist.get_text(self.updatedListSelectedVMRow, self.updatedListSelectedVMColumn)
		    		     
	    self.VMsInUpdatedGroupClist.remove(self.updatedListSelectedVMRow)
		    
	    self.universalVMList.append([selectedVM])
		    
	    self.totalVMsInUpdatedGroup = self.totalVMsInUpdatedGroup - 1
		    
	    if self.totalVMsInUpdatedGroup < 0:
	        self.totalVMsInUpdatedGroup = 0
		    
	    self.universalVMList.select_row(0,0)
	    self.VMsInUpdatedGroupClist.select_row(0,0)
	    
	    return
        
    
    def UpdateAffinityGroup(self, data=None):
       
        try:
        	
        	# VMList count validation (Minimum 2 vms must be selected)
        	if self.totalVMsInUpdatedGroup <= 1:
        		self.show_error_message("ERROR: Ideally 2 or more virtual machines should be in an Affinity Group.")
        		return
            
            # Create rule.
            
        	self.hide_error_message()
        	
        	# get group name.
        	
        	groupName = self.allGroupsClist.get_text(self.selectedGroupRow, self.selectedGroupColumn)
        	
        	# form old list.
        	
        	selectedGroupDetails = self.allGroupDictionary[groupName]
        	oldlist = selectedGroupDetails.getVMList()
        	
        	# form new list.
        	
        	newlist = []
        	for i in range(self.totalVMsInUpdatedGroup):
        		#self.err.show_info(_("Affinity Rule Successfully Created !!!"), "", "Rule Creation Success", False)
        		newlist.append(self.VMsInUpdatedGroupClist.get_text(i, 0))
        	
        	# call refresh group method.
        	
        	vmaffinityxmlutil.RefreshGroup(oldlist, newlist, groupName)
        
        except Exception, e:
            self.err.show_err(_("Error Updating Affinity Rule: %s") % str(e))
            return
                            
        # show success pop-up.
        self.err.show_info(_("Affinity Rule Successfully Updated !!!"), "", "Rule Updation Success", False)
        
        # close window.
        self.close(None, None)   

        return
    
    def update_universalVMList(self, memberVMs):
        
        # TODO: Sandeep - call amar's method, pass all vm list and current group vm list
        # Initialize with list return by amar's method.
        
        # clear current contents
        self.universalVMList.clear()
        
        universalVMs = self.findremainingvms(self.get_allVMsInMachine(), memberVMs)
        
        for vm in universalVMs:
            self.universalVMList.append([vm])
        
        # default selection
        self.universalVMList.select_row(0,0)
        
        return
    
    def update_VMsInUpdatedGroupClist(self, memberVMs):
    	
    	self.VMsInUpdatedGroupClist.clear()
    	self.totalVMsInUpdatedGroup = 0
    	
    	for vm in memberVMs:
    		self.VMsInUpdatedGroupClist.append([vm])
    		self.totalVMsInUpdatedGroup = self.totalVMsInUpdatedGroup + 1
    	
    	self.VMsInUpdatedGroupClist.select_row(0,0)
    	return
    
    
    def get_allVMsInMachine(self):
        connection = libvirt.open('qemu:///system')
        
        allVMsInMachine = []
        allVMsInMachine = connection.listDefinedDomains()
        
        # Just for testing TODO: SHOULD BE REMOVED.
        
        allVMsInMachine.append("vmaffinity3")
        allVMsInMachine.append("vmaffinity4")
        allVMsInMachine.append("vmaffinity5")
        
        return allVMsInMachine
    
    def findremainingvms(self, fulllist, oldlist):
	    
	    for vm in oldlist:
		    if fulllist.count(vm)==1:
		        fulllist.remove(vm)
	    
	    return fulllist
	    
vmmGObjectUI.type_register(vmaffinityManageRules)
