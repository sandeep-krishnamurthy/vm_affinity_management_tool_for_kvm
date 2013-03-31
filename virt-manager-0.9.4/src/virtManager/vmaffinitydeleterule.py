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

class vmaffinityDeleteRule(vmmGObjectUI):
    
    #initialization code
    def __init__(self):
        
        # check if groups config file exists
        vmaffinityxmlutil.checkIfGroupsConfigExists()

        #initialize all UI components to none
        self.vmaDeleteruleBanner = None
        self.configuredAffinityRulesScrolledwindow = None
        self.selectedAffinityRuleVMsScrolledwindow = None
        self.selectedRuleDesTextview = None
        self.cancelRuleDeletionButton = None
        self.DeleteRuleButton = None
        self.errorLabel = None
       
        self.allGroupsClist = None
        self.VMsInGroupClist = None       
        
        #CList related variables
        self.selectedGroupRow = None
        self.selectedGroupColumn = None
        
        self.allGroupDictionary = None
        
        vmmGObjectUI.__init__(self, "vmaffinity-deleterule.ui", "vmaffinity-deleterule")

        #Connect signals
        self.window.connect_signals({
            "on_cancelRuleDeletionButton_clicked": self.close,
            "on_DeleteRuleButton_clicked":self.deleteAffinityRuleButtonClicked,
            "on_vmaffinity-deleterule_delete_event": self.close,})
        
        #Initialize all UI components
        self.initUIComponents()
        

        self.err = vmmErrorDialog()
        
    def reset_state(self):
        
        # check if groups config file exists
        vmaffinityxmlutil.checkIfGroupsConfigExists()

        #initialize all UI components to none
        self.vmaDeleteruleBanner = None
        self.configuredAffinityRulesScrolledwindow = None
        self.selectedAffinityRuleVMsScrolledwindow = None
        self.selectedRuleDesTextview = None
        self.cancelRuleDeletionButton = None
        self.DeleteRuleButton = None
        self.errorLabel = None
       
        self.allGroupsClist = None
        self.VMsInGroupClist = None       
        
        #CList related variables
        self.selectedGroupRow = None
        self.selectedGroupColumn = None
        
        self.allGroupDictionary = None
        
        vmmGObjectUI.__init__(self, "vmaffinity-deleterule.ui", "vmaffinity-deleterule")

        #Connect signals
        self.window.connect_signals({
            "on_cancelRuleDeletionButton_clicked": self.close,
            "on_DeleteRuleButton_clicked":self.deleteAffinityRuleButtonClicked,
            "on_vmaffinity-deleterule_delete_event": self.close,})
        
        #Initialize all UI components
        self.initUIComponents()
        

        self.err = vmmErrorDialog()
       
    def initUIComponents(self):
        
        self.vmaDeleteruleBanner = self.widget("vmaDeleteruleBanner")
        self.configuredAffinityRulesScrolledwindow = self.widget("configuredAffinityRulesScrolledwindow")
        self.selectedAffinityRuleVMsScrolledwindow = self.widget("selectedAffinityRuleVMsScrolledwindow")
        self.selectedRuleDesTextview = self.widget("selectedRuleDesTextview")
        self.cancelRuleDeletionButton = self.widget("cancelRuleDeletionButton")
        self.DeleteRuleButton = self.widget("DeleteRuleButton")
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
        self.vmaDeleteruleBanner.set_from_file("/usr/local/share/virt-manager/icons/hicolor/16x16/actions/vmaffinitydeleterule.png")
    
    def init_allGroupsClist(self):
        #TODO: Sandeep - Call dictionary method here, initialize dictionary object and append all groups c list.
        
        self.allGroupsClist.clear()
        
        self.allGroupDictionary = vmaffinityxmlutil.getAffinityGroupDetails()
        groupsCount = len(self.allGroupDictionary)
        if groupsCount == 0:
            return
        
        for group in self.allGroupDictionary.keys():
            self.allGroupsClist.append([group])
        
        # default selection.
        self.allGroupsClist.select_row(0,0)
        pass
        
    def init_VMsInGroupClist(self):
        #TODO: Sandeep - Initially set first dictionary entry, vmlist and description.
        self.VMsInGroupClist.clear()
        
        # If there are no groups at all nothing to do here.
        groupsCount = len(self.allGroupDictionary)
        if groupsCount == 0:
            return
        
        selectedGroupName = self.allGroupsClist.get_text(0,0)

        if(selectedGroupName == None):
            return
        
        # Get group details object.
        selectedGroupDetails = self.allGroupDictionary[selectedGroupName]
        
        # get description
        desc = ""
        if selectedGroupDetails.getDescription() != None:
        	desc = selectedGroupDetails.getDescription()
        	
        self.selectedRuleDesTextview.get_buffer().set_text(desc)
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
        desc = ""
        if selectedGroupDetails.getDescription() != None:
        	desc = selectedGroupDetails.getDescription()
        	
        self.selectedRuleDesTextview.get_buffer().set_text(desc)
        # get list of virtual machines in the group
        memberVMs = selectedGroupDetails.getVMList()
        
        for vm in memberVMs:
            self.VMsInGroupClist.append([vm])
            
    #Event Handlers
    
    def deleteAffinityRuleButtonClicked(self, data=None):
        #Add code here to read which group is selected, use dictionary, then
        # Get group details object.
        selectedGroupName = self.allGroupsClist.get_text(self.selectedGroupRow,self.selectedGroupColumn)
        selectedGroupDetails = self.allGroupDictionary[selectedGroupName]
        
        # get description
        desc = ""
        
        if selectedGroupDetails.getDescription() != None:
        	desc = selectedGroupDetails.getDescription()
        	
        self.selectedRuleDesTextview.get_buffer().set_text(desc)
        # get list of virtual machines in the group
        memberVMs = selectedGroupDetails.getVMList()
        
        try:
            # 1. Delete from group configuration file, 
		    vmaffinityxmlutil.updateDeleteRuleGroupsXML(selectedGroupName)
		    # 2. Take all vm names, use dictionary, go to respective files and delete group membership.
		    vmaffinityxmlutil.updateDeleteRuleVM_XML(selectedGroupName, memberVMs)
        
        except Exception, e:
            self.err.show_err(_("Error deleting Affinity Rule: %s") % str(e))
            return
                            
        # show success pop-up.
        self.err.show_info(_("Affinity Rule Successfully Deleted !!!"), "", "Rule Deletion Success", False)
        
        # close window.
        self.close(None, None)    
        
    def show(self, parent):
        logging.debug("Showing vmaffinity delete affinity rule window")       
        self.topwin.set_transient_for(parent)
        self.topwin.present()


    def close(self, src_ignore=None, src2_ignore=None):
        
        logging.debug("Closing vmaffinity delete affinity rule window")
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
  
vmmGObjectUI.type_register(vmaffinityDeleteRule)
    
