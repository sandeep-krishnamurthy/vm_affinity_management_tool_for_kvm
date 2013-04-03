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

import xml.etree.ElementTree as ET
import os


##################################
######## Pre-Computation #########
##################################

def checkIfGroupsConfigExists():
	groupsXMLConfig = "/usr/local/share/virt-manager/AffinityGroups.xml"
	
	try:
		fp = open(groupsXMLConfig, "r")
		fp.close()
	except Exception, e:
		fp=open(groupsXMLConfig,'w+')
		fp.write('<VMAffinityGroups></VMAffinityGroups>')
		fp.close()

def loadGroupsToList():
                #TODO: Use configuration.filepath, don't use hard coded path
                doc = ET.parse("/usr/local/share/virt-manager/AffinityGroups.xml")
                s = doc.getroot()
                l=[]
                sortedlist = []
                for item in s:
                                l.append(item.attrib['name'])
                                sortedlist = mergesort(l)
                return sortedlist

def clearGroupsList(l): 
                if(l is not None):
                                        l=None

def search(list,key,low,high):
                        while(low<=high):
                                                middle=(low+high)/2
                                                if(key == list[middle] or key.lower() == (list[middle]).lower()):
                                                                return 'SUCCESS'
                                                else:
                                                                k=0
                                                                s=list[middle]
                                                                while(s[k] is key[k]):
                                                                                k=k+1
                                                                                if(k==len(s)):
                                                                                                break
                                                                                if(k==len(key)):
                                                                                                break
                                                                if(k<len(s) and k<len(key)):
                                                                                if(ord(s[k]) < ord(key[k])):
                                                                                                low=middle+1
                                                                                else:
                                                                                                high=middle-1
                                                                elif(k==len(s)):
                                                                                                low=middle+1   
                                                                else:
                                                                                                high=middle-1
                        return 'FAILURE'

def merge(left, right):
                                result = []
                                i, j = 0, 0
                                while(i < len(left) and j< len(right)):
                                        s1=left[i]
                                        s2=right[j]
                                        k=0
                                        while(s1[k] is s2[k]):
                                                        k=k+1
                                                        if(k==len(s1)):
                                                           break
                                                        if(k==len(s2)):
                                                           break
                                        if(k<len(s1) and k<len(s2)):
                                                if(ord(s1[k]) < ord(s2[k])):
                                                                result.append(left[i])
                                                                i=i+1
                                                else:
                                                                        result.append(right[j])
                                                                        j=j+1
                                        elif(k==len(s1)):
                                                        result.append(left[i])
                                                        i=i+1
                                        else:
                                                        result.append(right[j])
                                                        j=j+1
                                result += left[i:]
                                result += right[j:]
                                return result
                                
def mergesort(list):
                                if len(list) < 2:
                                        return list
                                middle = len(list) / 2
                                left = mergesort(list[:middle])
                                right = mergesort(list[middle:])
                                return merge(left, right)

##############################################
######## New Affinity Rules Creation #########
##############################################

# Updating "Groups.xml" configuration file.
def updateCreateRuleGroupsXML(groupName, VMlist, description):
                           #TODO: Use configuration.filepath, don't use hard coded path
                                doc = ET.parse("/usr/local/share/virt-manager/AffinityGroups.xml")
                                s = doc.getroot()
                                myattributes={"name": groupName}                
                                ET.SubElement(s,'group',attrib=myattributes)
                                #TODO: Use configuration.filepath, don't use hard coded path
                                doc.write('/usr/local/share/virt-manager/AffinityGroups.xml')
                                groups=doc.findall("group")
                                descriptionTag=ET.SubElement(groups[len(groups)-1],"Description")
                                descriptionTag.text=description
                                for VMName in VMlist:
                                    VM=ET.SubElement(groups[len(groups)-1],"VM")
                                    VM.text=VMName
		
		                        #TODO: Use configuration.filepath, don't use hard coded path
                                doc.write('/usr/local/share/virt-manager/AffinityGroups.xml')
                                                                
# Update individual virtual machine xml files.
def updateCreationRuleVM_XML(groupName,L):
                                for VM in L:
                                                doc = ET.parse("/etc/libvirt/qemu/"+VM+".xml")
                                                s = doc.getroot()
                                                affinityTag=doc.findall("affinity")
                                                if len(affinityTag)==0:
                                                                affinity=ET.SubElement(s,'affinity')
                                                                group=ET.SubElement(affinity,'group')	
                                                                group.text=groupName  
                                                                doc.write("/etc/libvirt/qemu/"+VM+".xml")
                                                else :                        
                                                                group=ET.SubElement(affinityTag[0],'group')	
                                                                group.text=groupName  
                                                                doc.write("/etc/libvirt/qemu/"+VM+".xml") 


######################################
######## View Affinity Rules #########
######################################

                                                
################### 1. Dictionary generateAffinityGroupDetails() ################################
# Dictionary : key = group name
# value = groupDetailsObject => GroupDetailsClass = description, list of vms

def getAffinityGroupDetails():
                                doc=ET.parse("/usr/local/share/virt-manager/AffinityGroups.xml")
                                s=doc.getroot()   
                                #L=[] 
                                dictionary = {}
                                for groups in s.findall("group"):
                                                                #d={}
                                                                description=groups.find("Description")
                                                                VMs=[]
                                                                for VM in groups.findall("VM"):
                                                                                VMs.append(VM.text)  
                                                                GroupDetailsObject=GroupDetails()
                                                                if description == None:
                                                                    data = ""
                                                                else:
                                                                    data = description.text
                                                                #detail=GroupDetailsObject.groupdetails(data,VMs)  
                                                                GroupDetailsObject.groupdetails(data, VMs)
                                                                groupName=groups.attrib['name']            
                                                                #d[groupName]=detail
                                                                dictionary[groupName] = GroupDetailsObject
                                                                #L.append(d)
                                #return L
                                return dictionary

class GroupDetails:
        
        def __init__(self):
            self.description = ""
            self.vmList = []
                
        def groupdetails(self, description,L):
            self.description = description
            self.vmList = L
                #detail=[]
                                #detail.append(description)
                                #detail.append(L)
                #	return detail
            return self
        
        def getDescription(self):
            return self.description
        
        def getVMList(self):
            return self.vmList
                                
######################################
######## Delete Affinity Rules #######
######################################

# Update "AffinityGroups.xml" configuration file.
def updateDeleteRuleGroupsXML(groupName):
                                                 VMs=[]
                                                 #TODO: Use configuration.filepath, don't use hard coded path
                                                 doc=ET.parse("/usr/local/share/virt-manager/AffinityGroups.xml")
                                                 s=doc.getroot()
                                                 for group in doc.findall("group"):
                                                                   if group.attrib['name']==groupName:
                                                                                for VM in group.findall("VM"):
                                                                                        VMs.append(VM.text)  
                                                                                s.remove(group)
                                                                                #TODO: Use configuration.filepath, don't use hard coded path
                                                                                doc.write('/usr/local/share/virt-manager/AffinityGroups.xml')  
                                                                                return VMs

# Update individula virtual machine xml configuration file
def updateDeleteRuleVM_XML(groupName,L):     
                                for VM in L:
                                                doc=ET.parse("/etc/libvirt/qemu/"+VM+".xml")
                                                s=doc.getroot()
                                                affinity=s.find("affinity")
                                                for group in affinity.findall("group"):
                                                                if(group.text==groupName):
                                                                                affinity.remove(group)
                                                                                doc.write("/etc/libvirt/qemu/"+VM+".xml")
                                                groups=affinity.findall("group")
                                                if(len(groups)==0):
                                                                s.remove(affinity)

######################################
######## Manage Affinity Rules #######
######################################

def updateGroupConfig(VMNameList, GroupName):
	tree = ET.parse('/usr/local/share/virt-manager/AffinityGroups.xml')
	root = tree.getroot()	
	for entry in root.findall('group'):
		name=entry.get('name')
		if name==GroupName:
			#print name
			for vms in entry.findall('VM'):
				#print vms.text				
				entry.remove(vms)		
			for vmss in VMNameList:
				VM=ET.SubElement(entry,'VM')
				VM.text=vmss				
			break
	tree.write('/usr/local/share/virt-manager/AffinityGroups.xml')
	return True

def removeGroupFromVMConfig(vmpath, groupname):
	tree = ET.parse(vmpath)
	root = tree.getroot()
	flag=1
	affinity=root.find('affinity')
	for entry in affinity.findall('group'):
		group=entry.text
		if group==groupname:
			affinity.remove(entry)
			flag=0
			break
	tree.write(vmpath)
	if flag==0:
		return True
	else:
		return False

def addGroupToVMConfig(vmpath, groupname):
	tree = ET.parse(vmpath)
	root = tree.getroot()
	affinity=root.find('affinity')
	group=ET.SubElement(affinity,'group')
	group.text=groupname
	tree.write(vmpath)
	return True

def RefreshGroup(oldlist,newlist,groupname):
	updateGroupConfig(newlist,groupname)
	for vms in oldlist:
		if(newlist.count(vms)==0):
			removeGroupFromVMConfig("/etc/libvirt/qemu/"+vms+".xml",groupname)
		else:
			newlist.remove(vms)
	for vms in newlist:
		addGroupToVMConfig("/etc/libvirt/qemu/"+vms+".xml",groupname)
	return True

############################
######## Migration #########
############################

def isVMAffineToOtherVM(vmname):
	doc=ET.parse("/etc/libvirt/qemu/"+vmname+".xml")
	s=doc.getroot()
	affinity=s.find("affinity")
	if affinity == None:
		return False
		
	if(len(affinity)==0):
		return False
	else:
		return True
		
##########################################################################################
####### Updating Groups Configuration whenever a vm is deleted or migrated from machine ##
##########################################################################################

def update_GroupsconfigOnDelete(VM):
	doc = ET.parse("/usr/local/share/virt-manager/AffinityGroups.xml")
	s = doc.getroot()
	for group in s.findall("group"):
		for vm in group.findall("VM"):
			if(vm.text == VM):
				group.remove(vm)
				doc.write('/usr/local/share/virt-manager/AffinityGroups.xml')
		vms=group.findall("VM")
		if(len(vms) <= 1):
			s.remove(group)
			doc.write('/usr/local/share/virt-manager/AffinityGroups.xml')
			

##########################################################################################
####### Checks if there exists a group with member vms same as new group to be created ###
##########################################################################################
def check_if_Rule_Duplicate(memberVMs):

	doc=ET.parse("/usr/local/share/virt-manager/AffinityGroups.xml")
	s=doc.getroot()
	for group in doc.findall("group"):
		VMs = []
		for VM in group.findall("VM"):
			VMs.append(VM.text)
		common = set(memberVMs) & set(VMs)
		if(len(common) == len(memberVMs)):
			return group.attrib['name']
			
	return None	
