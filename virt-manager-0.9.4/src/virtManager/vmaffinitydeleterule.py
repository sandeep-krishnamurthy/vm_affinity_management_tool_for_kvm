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

class vmaffinityDeleteRule(vmmGObjectUI):
    
    #initialization code
    def __init__(self):
        
        #initialize all UI components to none
        self.vmaDeleteruleBanner = None
        self.configuredAffinityRuleScrolledWindow = None
        self.selectedAffinityGroupVMsScrolledWindow = None
        self.selectedAffinityGroupDescTextView = None
        self.cancelButton = None
        self.deleteRuleButton = None
        self.errorMessageLabel = None
        self.affinityRulesCList = None
        self.memberVMsCList = None
        
        #Affinity Rule Group CList Info
        self.selectedAffinityGroupRow = None
        self.selectedAffinityGroupColumn = None
        self.selectedAffinityGroupName = None
        
        vmmGObjectUI.__init__(self, "vmaffinity-deleterule.ui", "vmaffinity-deleterule")

        #Connect signals
        self.window.connect_signals({
            "on_cancelNewRuleDeletionButton_clicked": self.cancelButtonClicked,
            "on_DeleteRuleButton_clicked":self.deleteAffinityRuleButtonClicked,
            "on_vmaffinity-deleterule_delete_event": self.close,})
        
        #Initialize all UI components
        self.initUIComponents()
    
    def initUIComponents(self):
        
        self.vmaDeleteruleBanner = self.widget("vmaDeleteruleBanner")
        self.configuredAffinityRuleScrolledWindow = self.widget("configuredAffinityRulesScrolledwindow")
        self.selectedAffinityGroupVMsScrolledWindow = self.widget("selectedAffinityRuleVMsScrolledwindow")
        self.selectedAffinityGroupDescTextView = self.widget("selectedRuleDesTextview")
        self.cancelButton = self.widget("cancelRuleDeletionButton")
        self.deleteRuleButton = self.widget("DeleteRuleButton")
        self.errorMessageLabel = self.widget("errorLabel")
        
        # Initialize CList objects.
        self.affinityRulesCList = gtk.CList(1,"affinityRulesClist")
        self.memberVMsCList = gtk.CList(1,"memberVMsCList")
        
        self.affinityRulesCList.set_shadow_type(gtk.SHADOW_OUT)
        self.affinityRulesCList.column_titles_hide()
        self.affinityRulesCList.set_column_width(0, 150)
        self.affinityRulesCList.connect("select_row", self.affinityRulesCList_row_selected)
        self.affinityRulesCList.show()        
        self.configuredAffinityRuleScrolledWindow.add(self.affinityRulesCList)
        
        self.memberVMsCList.set_shadow_type(gtk.SHADOW_OUT)
        self.memberVMsCList.column_titles_hide()
        self.memberVMsCList.set_column_width(0, 150)
        self.memberVMsCList.connect("select_row", self.memberVMsCList_row_selected)
        self.memberVMsCList.show()
        self.selectedAffinityGroupVMsScrolledWindow.add(self.memberVMsCList)
        
        #initialize all the UI Components.
        self.init_banner()
        self.init_affinityRulesCList()
        self.init_memberVMsCList()
        self.init_errorMessage()
        
                
    def init_banner(self):
        self.vmaDeleteruleBanner.set_from_file("/usr/local/share/virt-manager/icons/hicolor/16x16/actions/vmaffinitydeleterule.png")
    
    def init_affinityRulesCList(self):
        # Write Code here to build a dictionary of affinity groups and related virtual machines. Read from XML, handle exceptions.
        pass
    
    def init_memberVMsCList(self):
        #Write code here to have VM of first selected affinity group. Read from dictionary built in previous function.
        pass
        
    def init_errorMessage(self):
        #Initially error message should be empty and error label should be invisible.
        self.errorMessageLabel.set_text("")
        self.errorMessageLabel.hide()
    
    #Event Handlers
    def cancelButtonClicked(self, data=None):
        logging.debug("Cancelling deletion of affinity rule")
        self.close()
        pass
    
    def deleteAffinityRuleButtonClicked(self, data=None):
        #Add code here to read which group is selected, use dictionary, then
        # 1. Delete from group configuration file, 
        # 2. Take all vm names, use dictionary, go to respective files and delete group membership.
        pass
        
    def affinityRulesCList_row_selected(self, clist, row, column, event, data=None):

        self.selectedAffinityGroupRow = row
        self.selectedAffinityGroupColumn = column
        self.selectedAffinityGroupName = self.affinityRulesCList.get_text(row, column)
        
        #Write code here to read from dictionary and corresponding vms and update 1. descTextView 2. memberVMsClist
        
        return

    def memberVMsCList_row_selected(self, clist, row, column, event, data=None):
        #do nothing
        
        return
        
    def show(self, parent):
        logging.debug("Showing vmaffinity delete affinity rule window")       
        self.topwin.set_transient_for(parent)
        self.topwin.present()

    def close(self):
        logging.debug("Closing vmaffinity delete affinity rule window")
        self.topwin.hide()
        return 1
        
    def _cleanup(self):
        pass
    
    def show_error_message(self, data):
        
        self.errorMessageLabel.set_visible(True)
        self.errorMessageLabel.set_text(data)
        #self.warningLabel.set_text("you selected : " + str(self.selectedGroupVMRow) + str(self.selectedGroupVMColumn))
    
    def hide_error_message(self):
        self.errorMessageLabel.set_text("")
        self.errorMessageLabel.set_visible(False)
            
    #Helper Methods
    
    #Builds file path of the xml configuration file of the virtual machine, using only its name
    def get_VM_Conf_path(self, vmName):
        pass
        
vmmGObjectUI.type_register(vmaffinityDeleteRule)
    
