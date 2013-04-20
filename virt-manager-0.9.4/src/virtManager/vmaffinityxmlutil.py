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

def loadGroupsToList():
                #TODO: Use configuration.filepath, don't use hard coded path
                groupsXMLConfig = getGroupConfigFullPath()
                doc = ET.parse(groupsXMLConfig)
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
                                groupsXMLConfig = getGroupConfigFullPath()
                                doc = ET.parse(groupsXMLConfig)
                                s = doc.getroot()
                                myattributes={"name": groupName}                
                                ET.SubElement(s,'group',attrib=myattributes)
                                doc.write(groupsXMLConfig)
                                groups=doc.findall("group")
                                descriptionTag=ET.SubElement(groups[len(groups)-1],"Description")
                                descriptionTag.text=description
                                for VMName in VMlist:
                                    VM=ET.SubElement(groups[len(groups)-1],"VM")
                                    VM.text=VMName
		
                                doc.write(groupsXMLConfig)                          
# Update individual virtual machine xml files.
def updateCreationRuleVM_XML(groupName,L):
                                
                                for VM in L:
                                                
                                                doc = ET.parse(getVMConfigFullPathFromName(VM))
                                                s = doc.getroot()
                                                affinityTag=doc.findall("affinity")
                                                if len(affinityTag)==0:
                                                                affinity=ET.SubElement(s,'affinity')
                                                                group=ET.SubElement(affinity,'group')	
                                                                group.text=groupName  
                                                                doc.write(getVMConfigFullPathFromName(VM))
                                                else :                        
                                                                group=ET.SubElement(affinityTag[0],'group')	
                                                                group.text=groupName  
                                                                doc.write(getVMConfigFullPathFromName(VM)) 


######################################
######## View Affinity Rules #########
######################################

                                                
################### 1. Dictionary generateAffinityGroupDetails() ################################
# Dictionary : key = group name
# value = groupDetailsObject => GroupDetailsClass = description, list of vms

def getAffinityGroupDetails():
                                groupsXMLConfig = getGroupConfigFullPath()
                                doc=ET.parse(groupsXMLConfig)
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
                                                 groupsXMLConfig = getGroupConfigFullPath()
                                                 doc=ET.parse(groupsXMLConfig)
                                                 s=doc.getroot()
                                                 for group in doc.findall("group"):
                                                                   if group.attrib['name']==groupName:
                                                                                for VM in group.findall("VM"):
                                                                                        VMs.append(VM.text)  
                                                                                s.remove(group)
                                                                                doc.write(groupsXMLConfig)
                                                                                return VMs

# Update individula virtual machine xml configuration file
def updateDeleteRuleVM_XML(groupName,L):     
                                for VM in L:
                                                doc=ET.parse(getVMConfigFullPathFromName(VM))
                                                s=doc.getroot()
                                                affinity=s.find("affinity")
                                                for group in affinity.findall("group"):
                                                                if(group.text==groupName):
                                                                                affinity.remove(group)
                                                                                doc.write(getVMConfigFullPathFromName(VM))
                                                groups=affinity.findall("group")
                                                if(len(groups)==0):
                                                                s.remove(affinity)

######################################
######## Manage Affinity Rules #######
######################################

def updateGroupConfig(VMNameList, GroupName):
	groupsXMLConfig = getGroupConfigFullPath()
	tree = ET.parse(groupsXMLConfig)
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
	tree.write(groupsXMLConfig)
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
			removeGroupFromVMConfig(getVMConfigFullPathFromName(vms),groupname)
		else:
			newlist.remove(vms)
	for vms in newlist:
		addGroupToVMConfig(getVMConfigFullPathFromName(vms),groupname)
	return True

############################
######## Migration #########
############################

def isVMAffineToOtherVM(vmname):
	doc=ET.parse(getVMConfigFullPathFromName(vmname))
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
	groupsXMLConfig = getGroupConfigFullPath()
	doc = ET.parse(groupsXMLConfig)
	s = doc.getroot()
	for group in s.findall("group"):
		for vm in group.findall("VM"):
			if(vm.text == VM):
				group.remove(vm)
				doc.write(groupsXMLConfig)
		vms=group.findall("VM")
		if(len(vms) <= 1):
			s.remove(group)
			doc.write(groupsXMLConfig)
			

##########################################################################################
####### Checks if there exists a group with member vms same as new group to be created ###
##########################################################################################
def check_if_Rule_Duplicate(memberVMs):
	groupsXMLConfig = getGroupConfigFullPath()
	doc = ET.parse(groupsXMLConfig)
	s=doc.getroot()
	for group in doc.findall("group"):
		VMs = []
		for VM in group.findall("VM"):
			VMs.append(VM.text)
		common = set(memberVMs) & set(VMs)
		if(len(common) == len(memberVMs)):
			return group.attrib['name']
			
	return None	

###############################################
######### Create Host Affinity Rule ###########
###############################################

# Update VM-Host Affinity in Groups Config file.
def updateGroupConfigForHostAffinity(vmname, Description, affinedhostlist):
	
	groupConfigFullPath = getGroupConfigFullPath()
	doc=ET.parse(groupConfigFullPath)
	s=doc.getroot()
	if(len(s.findall("hostaffinity"))>0):
		for hostAffinity in s.findall("hostaffinity"):
			if(hostAffinity.attrib['name']==vmname):
				hostList=[]			
				for hosts in hostAffinity.findall("host"):
					hostList.append(hosts.text)
				newList=list(set(affinedhostlist)-set(hostList))
				print newList
				
				for newhost in newList:
					host=ET.SubElement(hostAffinity,"host")
                    			host.text=newhost
                    			doc.write(groupConfigFullPath)
				return
	
	myattributes={"name": vmname}                
	hostaffinity=ET.SubElement(s,'hostaffinity',attrib=myattributes)
	description=ET.SubElement(hostaffinity,"description")
	description.text=Description
	doc.write(groupConfigFullPath)		
	for newhost in affinedhostlist:
		host=ET.SubElement(hostaffinity,"host")
                host.text=newhost
                doc.write(groupConfigFullPath)

# Update VM-Host affinity rule in individual VM name.
def updateVMConfigForHostAffinity(vmname, Description, affinedhostlist):
	doc=ET.parse(getVMConfigFullPathFromName(vmname))
	s=doc.getroot()
	hostAffinity=s.find("hostaffinity")
	if(hostAffinity != None and len(hostAffinity)>0):
		existing_hosts=[]
		for hosts in hostAffinity.findall("host"):
			existing_hosts.append(hosts.text)
		total_hosts=list(set(affinedhostlist)-set(existing_hosts))       		
		for newhost in total_hosts:
			host=ET.SubElement(hostAffinity,"host")
                	host.text=newhost
                	doc.write(getVMConfigFullPathFromName(vmname))
		return
	hostaffinity=ET.SubElement(s,'hostaffinity')
	description=ET.SubElement(hostaffinity,"description")
	description.text=Description
	doc.write(getVMConfigFullPathFromName(vmname))		
	for newhost in affinedhostlist:
		host=ET.SubElement(hostaffinity,"host")
                host.text=newhost
        	doc.write(getVMConfigFullPathFromName(vmname))

###############################################
######### Delete Host Affinity Rule ###########
###############################################

def removeHostAffinityFromVMConfig(vmname):
	doc=ET.parse(getVMConfigFullPathFromName(vmname))
	s=doc.getroot()
	hostAffinity=s.find("hostaffinity")
	if(len(hostAffinity)>0):
		s.remove(hostAffinity)
		doc.write(getVMConfigFullPathFromName(vmname))

def removeHostAffinityFromGroupConfig(vmname):
	groupConfigFullPath = getGroupConfigFullPath()
	doc=ET.parse(groupConfigFullPath)
	s=doc.getroot()
	for hostAffinity in s.findall("hostaffinity"):
		if(hostAffinity.attrib['name']==vmname):
			s.remove(hostAffinity)
			doc.write(groupConfigFullPath)

#################################################################
######### Get Host Affinity Rule Details as Dictionary###########
#################################################################

# Return dictionary of host affinity details of given list of vms.
def getHostAffinityDetailsDictionary(VMList):

	mydictionary = {}
		
	for vm in VMList:

		l = []	
		data = ""	
		doc=ET.parse(getVMConfigFullPathFromName(vm))
		s=doc.getroot()
		hostAffinityTag=s.find("hostaffinity")
		HostAffinityDetailsObject=HostAffinityDetails()
		if hostAffinityTag != None and len(hostAffinityTag) > 0:
			description=hostAffinityTag.find("description")
   			hosts=hostAffinityTag.findall("host")
   			for host in hosts:
   				l.append(host.text)
   		
   			if description == None:
   				data = ""
   			else:
   				data = description.text
     		
   			HostAffinityDetailsObject.hostAffinityDetails(data, l)
   			
   			tempDictionary = {vm:HostAffinityDetailsObject}
   			mydictionary.update(tempDictionary)
   			
   			#print data, "and", vm	
   			
  		else:       		
			data = ""
			HostAffinityDetailsObject.hostAffinityDetails(data, l)
   			tempDictionary = {vm:HostAffinityDetailsObject}
   			mydictionary.update(tempDictionary)
       
       	#mydictionary.update({vm:HostAffinityDetailsObject})
       	
	return mydictionary

# return affined host list for a given virtual machine, "vmname"
def getHostAffinityDetails(vmname):
	hostList=[]
	doc=ET.parse(getVMConfigFullPathFromName(vmname))
   	s=doc.getroot()
	hostAffinityTag=s.find("hostaffinity")
	if hostAffinityTag != None and len(hostAffinityTag) > 0:
		hosts=hostAffinityTag.findall("host")
		for host in hosts:
			hostList.append(host.text)
		
	return hostList

# Container class for Host affinity details	
class HostAffinityDetails:
        
        def __init__(self):
            self.description = ""
            self.hostList = []
                
        def hostAffinityDetails(self, description, L):
            self.description = description
            self.hostList = L
               
            return self
        
        def getDescription(self):
            return self.description
        
        def getHostList(self):
            return self.hostList

#############################################################################
########## Controlling Migration Based on VM-host Affinity Rules ############
#############################################################################
def isVMAffineToHost(vmname, destHost):
	hostList = []
	hostList = getHostAffinityDetails(vmname)
	
	# No affinity to any hosts
	if (len(hostList) == 0):
		return False
	
	# If it is affined to any hosts, then destHost is one among them, allow migration
	for host in hostList:
		if host == destHost:
			return False
	
	return True

################################################################
#######################Helper Methods###########################
################################################################
def checkIfGroupsConfigExists():
	groupsXMLConfig = getGroupConfigFullPath()
	
	try:
		fp = open(groupsXMLConfig, "r")
		fp.close()
	except Exception, e:
		fp=open(groupsXMLConfig,'w+')
		fp.write('<VMAffinityGroups></VMAffinityGroups>')
		fp.close()


def checkIfVMConfigExists(vmname):
	fullPath = getLocalConfigFolderPath() + vmname + ".xml"
	
	try:
		fp = open(fullPath, "r")
		fp.close()
	except Exception, e:
		fp = open(fullPath, "w+")
		fp.write("<vmaffinity><affinity></affinity></vmaffinity>")
		fp.close()


def getGroupConfigFullPath():
	return getLocalConfigFolderPath() + "AffinityGroups.xml"


def getVMConfigFullPathFromName(vmname):
	checkIfVMConfigExists(vmname)
	return getLocalConfigFolderPath() + vmname + ".xml"


def getLocalConfigFolderPath():
	return "/home/sandeep/vmaffinity_configuration/"
