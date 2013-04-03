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

from virtManager.baseclass import vmmGObjectUI
from virtManager import vmaffinityxmlutil
from virtManager.error import vmmErrorDialog

class vmaffinityCreateNewRule(vmmGObjectUI):
    
    # Initialization Code
    def __init__(self):
        
        # check if groups config file exists
        vmaffinityxmlutil.checkIfGroupsConfigExists()
        
        #initialize all UI components to none
        self.allVMScrolledWindow = None
        self.newGroupVMScrolledWindow = None
        self.newGroupTextEntry = None
        self.newGroupDescriptionTextView = None
        self.createNewRuleBanner = None
        self.addVMToGroupButton = None
        self.removeVMFromGroupButton = None
        self.cancelNewRuleCreationButton = None
        self.createNewRuleButton = None
        self.warningLabel = None
        self.allVMClist = None
        self.groupVMClist = None
        
        #CList related variables
        self.selectedAllVMRow = None
        self.selectedAllVMColumn = None
        self.selectedGroupVMRow = None
        self.selectedGroupVMColumn = None
        self.allVMList = None
        self.totalVMsInGroup = 0
        
        #Helper Variables
        self.sortedAllGroupsList = None
        
        vmmGObjectUI.__init__(self, "vmaffinity-createnewrule.ui", "vmaffinity-createnewrule")

        #Connect signals
        self.window.connect_signals({
            "on_addVMToAffinityGroupbutton_clicked": self.addVMToGroupClicked,
            "on_removeVMFromAffinityGroup_clicked": self.removeVMFromGroupClicked,
            "on_cancelNewRuleCreationButton_clicked":self.cancelClicked,
            "on_CreateNewRuleButton_clicked":self.createNewAffinityGroupClicked,
            "on_newAffinityGroupNameTextEntry_focus_out_event":self.groupNameTextEntryFocusOut,
            "on_vmaffinity-createnewrule_delete_event": self.close,
            })
        
        #Initialize UI components
        self.initUIComponents()
        
        #Initialize helper variables
        self.sortedAllGroupsList = vmaffinityxmlutil.loadGroupsToList()
        
    def initUIComponents(self):
    
        self.allVMScrolledWindow = self.widget("availableVirtualMachineScrolledwindow")
        self.newGroupVMScrolledWindow = self.widget("groupVirtualMachineScrolledwindow")
        self.newGroupTextEntry = self.widget("newAffinityGroupNameTextEntry")
        self.newGroupDescriptionTextView = self.widget("newRuleDescriptionTextView")
        self.createNewRuleBanner = self.widget("vma-createnewrule-banner")
        self.addVMToGroupButton = self.widget("addVMToAffinityGroupbutton")
        self.removeVMFromGroupButton = self.widget("removeVMFromAffinityGroup")
        self.cancelNewRuleCreationButton = self.widget("cancelNewRuleCreationButton")
        self.createNewRuleButton = self.widget("CreateNewRuleButton")
        self.warningLabel = self.widget("warningLabel")        
        
        #self.addVMToGroupButton.connect("clicked", self.addVMToGroupClicked)
        #create all virtual machine CList and vms in new group list.
        
        self.allVMClist = gtk.CList(1, "allVMClist")
        self.groupVMClist = gtk.CList(1, "GroupVMClist")
        
        self.allVMClist.set_shadow_type(gtk.SHADOW_OUT)
        self.allVMClist.column_titles_hide()
        self.allVMClist.set_column_width(0, 150)
        self.allVMClist.connect("select_row", self.allVMClist_row_selected)
        self.allVMClist.show()        
        self.allVMScrolledWindow.add(self.allVMClist)
        
        self.groupVMClist.set_shadow_type(gtk.SHADOW_OUT)
        self.groupVMClist.column_titles_hide()
        self.groupVMClist.set_column_width(0, 150)
        self.groupVMClist.connect("select_row", self.groupVMClist_row_selected)
        self.groupVMClist.show()
        self.newGroupVMScrolledWindow.add(self.groupVMClist)
        
        self.err = vmmErrorDialog()
        #initialize all the UI Components.
        self.init_banner()
        self.init_allVMList()
        self.init_groupVMList()
        self.init_errorMessage()
    
    def init_banner(self):
        self.createNewRuleBanner.set_from_file("/usr/local/share/virt-manager/icons/hicolor/16x16/actions/vmaffinitycreaterule.png")
    
    def init_allVMList(self):

        #### Temp starts
    	# TODO SANDEEP : Here write code to form list by fetching from libvirt instead of hardcoding.
        #vms = [ [ "vmaffinity1"],
             #     [ "vmaffinity2"],
              #    [ "vmaffinity3"],
              #    [ "vmaffinity4"],
				#  [	"vmaffinity5"],
				#  [	"vmaffinity6"],
				#  [	"vmaffinity7"]]
	    
	    # Here we do the actual adding of the text. It's done once for
        # each row.
        #for indx in range(7):
            #self.allVMClist.append(vms[indx])
        
        #default selection
        #self.allVMClist.select_row(0,0)
        #### Temp ends
        
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
        
        
        # just for testing
        #self.allVMClist.append(["vmaffinity1"])
		
		# Just for testing TODO: SHOULD BE REMOVED.
        
        #self.allVMClist.append(['vmaffinity3'])
        #self.allVMClist.append(['vmaffinity4'])
        #self.allVMClist.append(['vmaffinity5'])
        
        #default selection
        self.allVMClist.select_row(0,0)
        
        return
        
    def init_groupVMList(self):
		#Initially this list should be empty.
        self.groupVMClist.clear()
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
       
        self.groupVMClist.append([selectedVM])
        
        self.totalVMsInGroup = self.totalVMsInGroup + 1
        
        self.groupVMClist.select_row(0,0)
        self.allVMClist.select_row(0,0)  
        return
        
    def removeVMFromGroupClicked(self, data=None):
        
        selectedVM = self.groupVMClist.get_text(self.selectedGroupVMRow, self.selectedGroupVMColumn)
        
        self.groupVMClist.freeze()
        
        self.groupVMClist.remove(self.selectedAllVMRow)
        
        self.groupVMClist.thaw()
        
        #self.warningLabel.set_text("Remove event handler, row = %d, selected VM = %s\n " %(self.selectedAllVMRow, selectedVM))
       
        self.allVMClist.append([selectedVM])

        self.totalVMsInGroup = self.totalVMsInGroup - 1
        if self.totalVMsInGroup < 0:
            self.totalVMsInGroup = 0
        
        self.allVMClist.select_row(0,0)
        self.groupVMClist.select_row(0,0)
        return
    
    def groupNameTextEntryFocusOut(self, data=None):
        self.newGroupName = self.newGroupTextEntry.get_text()
        
        # check if empty
        if self.newGroupName == None or self.newGroupName == "":
            self.show_error_message("ERROR: Affinity Group Name Cannot be empty")
            return
        
        # check if duplicate
        if self.sortedAllGroupsList.count(self.newGroupName) != 0:
            self.show_error_message("ERROR: Affinity Group Name Already Exists. Please enter other name")
            return
        
        # Clear Any Error Messages
        self.hide_error_message()
        
    def cancelClicked(self, data=None):
        logging.debug("Cancelling creation of new affinity rule")
        self.close(None, None)
        return 1
        
    def createNewAffinityGroupClicked(self, data=None):
        
        # Group Name Validation
        self.newGroupName = self.newGroupTextEntry.get_text()
        
        # check if empty
        if self.newGroupName == None or self.newGroupName == "":
            self.show_error_message("ERROR: Affinity Group Name Cannot be empty")
            return
        
        # check if duplicate
        if self.sortedAllGroupsList.count(str(self.newGroupName)) != 0:
            self.show_error_message("ERROR: Affinity Group Name Already Exists. Please enter other name")
            return
                
        # get description
        text_buffer = self.newGroupDescriptionTextView.get_buffer()
        self.newGroupDescription = ""
        if text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter(), True) != None:
        	self.newGroupDescription = text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter(), True)
        
        # VMList count validation (Minimum 2 vms must be selected)
        if self.totalVMsInGroup <= 1:
            self.show_error_message("ERROR: Ideally 2 or more virtual machines should be in an Affinity Group.")
            return
        
        # Create rule
        self.hide_error_message()
        
        # build all vms in group.
        #vmsInGroup = []
        #for i in range(self.totalVMsInGroup):
         #   vmsInGroup.append(self.groupVMClist.get_text(i, 0))
            
        # update groups.xml configuration
        #group="anunag"
        #VM=['VM_Affinity1','VM_Affinity2']
        #description="Anusha-Nag Group"
        
        try:
            #vmsInGroup = []
            #vmsInGroup.append("asdf")
            #vmsInGroup.append("defg")
            
            # build all vms in group.
            vmsInGroup = []
            for i in range(self.totalVMsInGroup):
                vmsInGroup.append(self.groupVMClist.get_text(i, 0))
                
            # Update Groups config file.
            vmaffinityxmlutil.updateCreateRuleGroupsXML(str(self.newGroupName), vmsInGroup, str(self.newGroupDescription))    

            # Update individual vm config file.
            vmaffinityxmlutil.updateCreationRuleVM_XML(str(self.newGroupName), vmsInGroup)            
             
        except Exception, e:
            self.err.show_err(_("Error creating Affinity Rule: %s") % str(e))
            return
                            
        # show success pop-up.
        self.err.show_info(_("Affinity Rule Successfully Created !!!"), "", "Rule Creation Success", False)
        
        # close window.
        self.close(None, None)       
        
    
    # Helper Methods:
        
    def insertAffinityGroupInVM(self, filepath, affinityGroupName):
        pass  

    def close(self, src_ignore=None, src2_ignore=None):
        logging.debug("Closing vmaffinity create new affinity rule window")
        self.topwin.hide()
        
        self.reset_state()
		
        return 1
    
    def reset_state(self):
    	#initialize all UI components to none
        self.allVMScrolledWindow = None
        self.newGroupVMScrolledWindow = None
        self.newGroupTextEntry = None
        self.newGroupDescriptionTextView = None
        self.createNewRuleBanner = None
        self.addVMToGroupButton = None
        self.removeVMFromGroupButton = None
        self.cancelNewRuleCreationButton = None
        self.createNewRuleButton = None
        self.warningLabel = None
        self.allVMClist = None
        self.groupVMClist = None
        
        #CList related variables
        self.selectedAllVMRow = None
        self.selectedAllVMColumn = None
        self.selectedGroupVMRow = None
        self.selectedGroupVMColumn = None
        self.allVMList = None
        self.totalVMsInGroup = 0
        
        #Helper Variables
        self.sortedAllGroupsList = None
        
        vmmGObjectUI.__init__(self, "vmaffinity-createnewrule.ui", "vmaffinity-createnewrule")

        #Connect signals
        self.window.connect_signals({
            "on_addVMToAffinityGroupbutton_clicked": self.addVMToGroupClicked,
            "on_removeVMFromAffinityGroup_clicked": self.removeVMFromGroupClicked,
            "on_cancelNewRuleCreationButton_clicked":self.cancelClicked,
            "on_CreateNewRuleButton_clicked":self.createNewAffinityGroupClicked,
            "on_newAffinityGroupNameTextEntry_focus_out_event":self.groupNameTextEntryFocusOut,
            "on_vmaffinity-createnewrule_delete_event": self.close,
            })
        
        #Initialize UI components
        self.initUIComponents()
        
        #Initialize helper variables
        self.sortedAllGroupsList = vmaffinityxmlutil.loadGroupsToList()
    
    def show(self, parent):
        logging.debug("Showing vmaffinity create new affinity rule window")       
        self.topwin.set_transient_for(parent)
        self.topwin.present()


    def _cleanup(self):
        
        self.reset_state() 
    
    def allVMClist_row_selected(self, clist, row, column, event, data=None):
        self.selectedAllVMRow = row
        self.selectedAllVMColumn = column
        self.show_error_message()

    def groupVMClist_row_selected(self, clist, row, column, event, data=None):
        self.selectedGroupVMRow = row
        self.selectedGroupVMColumn = column

    def show_error_message(self, data):
        
        self.warningLabel.set_visible(True)
        self.warningLabel.set_text(data)
        #self.warningLabel.set_text("you selected : " + str(self.selectedGroupVMRow) + str(self.selectedGroupVMColumn))
    
    def hide_error_message(self):
    
        self.warningLabel.set_text("")
        self.warningLabel.set_visible(False)

vmmGObjectUI.type_register(vmaffinityCreateNewRule)
