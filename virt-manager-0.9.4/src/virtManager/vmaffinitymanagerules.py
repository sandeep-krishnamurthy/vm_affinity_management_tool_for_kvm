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
from virtManager import vmaffinityxmlutil
from virtManager.vmaffinityxmlutil import GroupDetails
from virtManager.error import vmmErrorDialog

class vmaffinityManageRules(vmmGObjectUI):
    
    # Initialization Code
    def __init__(self):
        
        #initialize all UI components to none        
        self.manageRuleBanner = None
        self.configuredAffinityRulesScrolledwindow = None
        self.selectedRuleDesTextview = None
        self.selectedAffinityRuleVMsScrolledwindow = None
        self.availableVirtualMachineScrolledwindow = None
        self.updatedGroupVirtualMachineScrolledwindow = None
        self.addVMToUpdatedAffinityGroupbutton = None
        self.removeVMFromUpdatedAffinityGroup = None
        self.cancelRuleManageButton = None
        self.UpdateAffinityGroupButton = None
        self.errorLabel = None
        
        self.allGroupsClist = None
        self.VMsInGroupClist = None  
        self.VMsInUpdatedGroupClist = None
        
        #CList related variables
        self.selectedGroupRow = None
        self.selectedGroupColumn = None
        
        self.allGroupDictionary = None
        
        vmmGObjectUI.__init__(self, "vmaffinity-manage-affinity-rules.ui", "vmaffinity-manage-affinity-rules")
        
        #Connect signals
        self.window.connect_signals({"on_addVMToUpdatedAffinityGroupbutton_clicked": self.addVMToUpdatedAffinityGroup,
        	"on_removeVMFromUpdatedAffinityGroup_clicked": self.removeVMFromUpdatedAffinityGroup,    				"on_cancelRuleManageButton_clicked": self.cancelRuleManagement, 
        	"on_UpdateAffinityGroupButton_clicked": self.UpdateAffinityGroup,
        })
		
		
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
        self.addVMToUpdatedAffinityGroupbutton = self.widget("")
        self.removeVMFromUpdatedAffinityGroup = self.widget("addVMToUpdatedAffinityGroupbutton")
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
        
        #initialize all the UI Components.
        self.init_banner()
        self.init_allGroupsClist()
        self.init_VMsInGroupClist()
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
        pass
        
    def init_VMsInGroupClist(self):
        #TODO: Sandeep - Initially set first dictionary entry, vmlist and description.
        self.VMsInGroupClist.clear()
        
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
        
        # get description
        
        self.selectedRuleDesTextview.get_buffer().set_text(selectedGroupDetails.getDescription())
        # get list of virtual machines in the group
        memberVMs = selectedGroupDetails.getVMList()
        
        for vm in memberVMs:
            self.VMsInGroupClist.append([vm])
    
    def show(self, parent):
        logging.debug("Showing vmaffinity manage affinity rule window")       
        self.topwin.set_transient_for(parent)
        self.topwin.present()

    def close(self, src_ignore=None, src2_ignore=None):
        logging.debug("Closing vmaffinity manage affinity rule window")
        self.topwin.hide()
        
        self.selectedGroupRow = None
        self.selectedGroupColumn = None
        
        self.allGroupDictionary = None
        self.allGroupsClist = None
        self.VMsInGroupClist = None 
        return 1
    
    def cancelClicked(self, data=None):
        self.close()
            
    def _cleanup(self):
        #CList related variables
        self.selectedGroupRow = None
        self.selectedGroupColumn = None
        
        self.allGroupDictionary = None
        self.allGroupsClist = None
        self.VMsInGroupClist = None    
    
    def show_error_message(self, data):
        
        self.errorLabel.set_visible(True)
        self.errorLabel.set_text(data)       
    
    def hide_error_message(self):
        self.errorLabel.set_text("")
        self.errorLabel.set_visible(False)
    
    def addVMToUpdatedAffinityGroup(self):
        pass
    
    def removeVMFromUpdatedAffinityGroup(self):
        pass
    
    def cancelRuleManagement(self):
        pass
    
    def UpdateAffinityGroup(self):
        pass
        
vmmGObjectUI.type_register(vmaffinityManageRules)
