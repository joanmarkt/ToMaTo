# -*- coding: utf-8 -*-

import config, host_store, topology_store
from host import Host
from topology import Topology
from log import Logger
from task import TaskStatus

import xmlrpclib

class Fault(xmlrpclib.Fault):
	UNKNOWN = -1
	NO_SUCH_TOPOLOGY = 100
	ACCESS_TO_TOPOLOGY_DENIED = 101
	NOT_A_REGULAR_USER = 102
	INVALID_TOPOLOGY_STATE_TRANSITION = 103
	IMPOSSIBLE_TOPOLOGY_CHANGE = 104
	NO_SUCH_HOST = 200
	NO_SUCH_HOST_GROUP = 201
	ACCESS_TO_HOST_DENIED = 202
	HOST_EXISTS = 203

class TopologyInfo():
	def __init__(self, topology):
		self.id = topology.id
		self.state = str(topology.state)
		self.is_created = self.state == TopologyState.CREATED
		self.is_uploaded = self.state == TopologyState.UPLOADED
		self.is_prepared = self.state == TopologyState.PREPARED
		self.is_started = self.state == TopologyState.STARTED
		self.owner = str(topology.owner)
		self.resource_usage = topology.resource_usage()

class HostInfo():
	def __init__(self, host):
		self.name = str(host.name)
		self.group = str(host.group)
		self.public_bridge = str(host.public_bridge)

logger = Logger(config.log_dir + "/api.log")

def _top_access(top_id, user=None):
	if topology_store.get(top_id).owner == user.username:
		return
	if user.is_admin:
		return
	raise Fault(Fault.ACCESS_TO_TOPOLOGY_DENIED, "access to topology %s denied" % top_id)

def _host_access(host_name, user=None):
	if not user.is_admin:
		raise Fault(Fault.ACCESS_TO_HOST_DENIED, "access to host %s denied" % host_name)
	
def top_info(id, user=None):
	logger.log("top_info(%s)" % id, user=user.username)
	return TopologyInfo(topology_store.get(id))

def top_list(filter_owner=None, filter_state=None, filter_host=None, user=None):
	logger.log("top_list(filter_owner=%s, filter_state=%s, filter_host=%s)" % (filter_owner, filter_state, filter_host), user=user.username)
	tops=[]
	for t in topology_store.topologies.values():
		if (filter_state==None or t.state==filter_state) and (filter_owner==None or t.owner==filter_owner) and (filter_host==None or filter_host in t.affected_hosts()):
			tops.append(TopologyInfo(t))
	return tops
	
def top_import(xml, user=None):
	logger.log("top_import()", user=user.username, bigmessage=xml)
	if not user.is_user:
		raise Fault(Fault.NOT_A_REGULAR_USER, "only regular users can create topologies")
	dom=minidom.parseString(xml)
	host_store.update_host_usage()
	top=Topology(dom,False)
	top.owner=user.username
	id=topology_store.add(top)
	return id
	
def top_change(top_id, xml, user=None):
	logger.log("top_change(%s)" % top_id, user=user.username, bigmessage=xml)
	_top_access(top_id, user)
	dom=minidom.parseString(xml)
	host_store.update_host_usage()
	newtop=Topology(dom,False)
	top = topology_store.get(top_id)
	return top.change(newtop)

def top_remove(top_id, user=None):
	logger.log("top_remove(%s)" % top_id, user=user.username)
	_top_access(top_id, user)
	topology_store.remove(top_id)
	return True
	
def top_prepare(top_id, user=None):
	logger.log("top_prepare(%s)" % top_id, user=user.username)
	_top_access(top_id, user)
	return topology_store.get(top_id).prepare()
	
def top_destroy(top_id, user=None):
	logger.log("top_destroy(%s)" % top_id, user=user.username)
	_top_access(top_id, user)
	return topology_store.get(top_id).destroy()
	
def top_upload(top_id, user=None):
	logger.log("top_upload(%s)" % top_id, user=user.username)
	_top_access(top_id, user)
	return topology_store.get(top_id).upload()
	
def top_start(top_id, user=None):
	logger.log("top_start(%s)" % top_id, user=user.username)
	_top_access(top_id, user)
	return topology_store.get(top_id).start()
	
def top_stop(top_id, user=None):
	logger.log("top_stop(%s)" % top_id, user=user.username)
	_top_access(top_id, user)
	return topology_store.get(top_id).stop()
	
def top_get(top_id, include_ids=False, user=None):
	logger.log("top_get(%s, include_ids=%s)" % (top_id, include_ids), user=user.username)
	_top_access(top_id, user)
	top=topology_store.get(top_id)
	dom=top.create_dom(include_ids)
	return dom.toprettyxml(indent="\t", newl="\n")
		
def host_list(group_filter=None, user=None):
	logger.log("host_list(group_filter=%s)" % group_filter, user=user.username)
	hosts=[]
	for h in host_store.hosts.values():
		if group_filter==None or h.group == group_filter:
			hosts.append(HostInfo(h))
	return hosts

def host_add(host_name, group_name, public_bridge, user=None):
	logger.log("host_add(%s,%s,%s)" % (host_name, group_name, public_bridge), user=user.username)
	_host_access(host_name,user)
	host=Host()
	host.name = host_name
	host.group = group_name
	host.public_bridge = public_bridge
	host.check()
	host_store.add(host)
	return True

def host_remove(host_name, user=None):
	logger.log("host_remove(%s)" % host_name, user=user.username)
	_host_access(host_name,user)
	host_store.remove(host_name)
	return True
		
def account(user=None):
	logger.log("account()", user=user.username)
	return user

def task_status(id, user=None):
	logger.log("task_status(%s)" % id, user=user.username)
	return TaskStatus.tasks[id].dict()
	
host_store.init()
topology_store.init()