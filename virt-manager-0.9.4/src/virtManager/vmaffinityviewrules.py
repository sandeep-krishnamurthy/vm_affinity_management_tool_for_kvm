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

class vmaffinityViewRules(vmmGObjectUI):
    
    # Initialization Code
    def __init__(self):
        
        # check if groups config file exists
        vmaffinityxmlutil.checkIfGroupsConfigExists()

        #initialize all UI components to none
        self.viewRulesImageBanner = None
        self.configuredAffinityRulesScrolledwindow = None
        self.selectedRuleDesTextview = None
        self.selectedAffinityRuleVMsScrolledwindow = None
        self.cancelViewRuleButton = None
        self.okViewRuleButton = None
        
        self.allGroupsClist = None
        self.VMsInGroupClist = None
        
        #CList related variables
        self.selectedGroupRow = None
        self.selectedGroupColumn = None
        
        self.allGroupDictionary = None
        
        #Initialize window
        vmmGObjectUI.__init__(self, "vmaffinity-view-rules.ui", "vmaffinity-view-rules")
        
        #Connect signals
        self.window.connect_signals({ 
        	"on_vmaffinity-view-configured-rules_delete_event":self.close,
        	"on_cancelViewRuleButton_clicked":self.close,
        	"on_okViewRuleButton_clicked":self.close,
        })
        
        #Initialize UI components
        self.initUIComponents()
        
        
    def initUIComponents(self):
        
        self.viewRulesImageBanner = self.widget("viewRulesImageBanner")
        self.configuredAffinityRulesScrolledwindow = self.widget("configuredAffinityRulesScrolledwindow")
        self.selectedRuleDesTextview = self.widget("selectedRuleDesTextview")
        self.selectedAffinityRuleVMsScrolledwindow = self.widget("selectedAffinityRuleVMsScrolledwindow")
        self.cancelViewRuleButton = self.widget("cancelViewRuleButton")
        self.okViewRuleButton = self.widget("okViewRuleButton")
        
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
        self.VMsInGroupClist.connect("select_row", self.VMsInGroupClist_row_selected)
        self.VMsInGroupClist.show()
        self.selectedAffinityRuleVMsScrolledwindow.add(self.VMsInGroupClist)
        
        #initialize all the UI Components.
        self.init_banner()
        self.init_allGroupsClist()
        self.init_VMsInGroupClist()

        
    def init_banner(self):	
	    #TODO:Sandeep - Create a new banner for view rule.
        self.viewRulesImageBanner.set_from_file("/usr/local/share/virt-manager/icons/hicolor/16x16/actions/vmaffinityviewrules.png")
    
    
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
        
        # If count of groups itself is zero there is nothing to do.
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
    
    def close(self, src_ignore=None, src2_ignore=None):
        logging.debug("Closing vmaffinity view affinity rules window")
        self.topwin.hide()
        
        self.reset_state()
        
        return 1
    
    def reset_state(self):
        
        #initialize all UI components to none
        self.viewRulesImageBanner = None
        self.configuredAffinityRulesScrolledwindow = None
        self.selectedRuleDesTextview = None
        self.selectedAffinityRuleVMsScrolledwindow = None
        self.cancelViewRuleButton = None
        self.okViewRuleButton = None
        
        self.allGroupsClist = None
        self.VMsInGroupClist = None
        
        #CList related variables
        self.selectedGroupRow = None
        self.selectedGroupColumn = None
        
        self.allGroupDictionary = None
        
        #Initialize window
        vmmGObjectUI.__init__(self, "vmaffinity-view-rules.ui", "vmaffinity-view-rules")
        
        #Connect signals
        self.window.connect_signals({ 
        	"on_vmaffinity-view-configured-rules_delete_event":self.close,
        	"on_cancelViewRuleButton_clicked":self.close,
        	"on_okViewRuleButton_clicked":self.close,
        })
        
        #Initialize UI components
        self.initUIComponents()
        
    def show(self, parent):
        logging.debug("Showing vmaffinity view affinity rules window")      
        self.topwin.set_transient_for(parent)
        self.topwin.present()        
       
    def _cleanup(self):
        self.reset_state()
    
    def VMsInGroupClist_row_selected(self, clist, row, column, event, data=None):
        pass

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
        
        
vmmGObjectUI.type_register(vmaffinityViewRules)        
