# -*- coding: utf-8 -*-

from django.db import models

import generic, hosts, fault, config, hashlib, re, util

class KVMDevice(generic.Device):
	kvm_id = models.IntegerField()
	template = models.CharField(max_length=30)
	vnc_port = models.IntegerField()
	
	def init(self, topology, dom):
		self.topology = topology
		self.decode_xml(dom)
		if not self.template:
			self.template = config.kvm_default_template
		self.host = hosts.get_best_host(self.hostgroup)
		self.kvm_id = self.host.next_free_vm_id()
		self.vnc_port = self.host.next_free_port()
		self.save()		
		for interface in dom.getElementsByTagName ( "interface" ):
			iface = generic.Interface()
			iface.init(self, interface)
			self.interfaces_add(iface)
	
	def upcast(self):
		return self

	def download_image(self, filename, task):
		pass

	def upload_image(self, filename, task):
		pass

	def encode_xml(self, dom, doc, internal):
		generic.Device.encode_xml(self, dom, doc, internal)
		dom.setAttribute("template", self.template)
		if internal:
			dom.setAttribute("kvm_id", self.kvm_id)
		
	def decode_xml(self, dom):
		generic.Device.decode_xml(self, dom)
		self.template = dom.getAttribute("template")

	def write_aux_files(self):
		"""
		Write the aux files for this object and its child objects
		"""		
		generic.Device.write_aux_files(self)

	def write_control_script(self, host, script, fd):
		"""
		Write the control script for this object and its child objects
		"""
		generic.Device.write_control_script(self, host, script, fd)
		if script == "prepare":
			fd.write("qm create %s\n" % self.kvm_id )
			fd.write("mkdir -p /var/lib/vz/images/%s\n" % self.kvm_id)
			fd.write("cp /var/lib/vz/template/qemu/%s /var/lib/vz/images/%s\n" % (self.template, self.kvm_id))
			fd.write("qm set %s --ide0 local:%s/%s\n" % (self.kvm_id, self.kvm_id, self.template))
			for iface in self.interfaces_all():
				iface_id = re.match("eth(\d+)", iface.name).group(1)
				bridge = self.bridge_name(iface)
				fd.write("qm set %s --vlan%s e1000\n" % ( self.kvm_id, iface_id ) )
		if script == "destroy":
			fd.write("qm destroy %s\n" % self.kvm_id)
			fd.write ( "true\n" )
		if script == "start":
			fd.write("qm start %s\n" % self.kvm_id)
			for iface in self.interfaces_all():
				iface_id = re.match("eth(\d+)", iface.name).group(1)
				bridge = self.bridge_name(iface)
				fd.write("brctl delif vmbr%s vmtab%si%s\n" % ( iface_id, self.kvm_id, iface_id ) )
				fd.write("brctl addbr %s\n" % bridge )
				fd.write("brctl addif %s vmtab%si%s\n" % ( bridge, self.kvm_id, iface_id ) )
				fd.write("ip link set %s up\n" % bridge )
			fd.write("( while true; do nc -l -p %s -c \"qm vncproxy %s %s 2>/dev/null\" ; done ) >/dev/null 2>&1 & echo $! > vnc-%s.pid\n" % ( self.vnc_port, self.kvm_id, self.vnc_password(), self.name ) )
		if script == "stop":
			fd.write("cat vnc-%s.pid | xargs kill\n" % self.name )
			fd.write("qm stop %s\n" % self.kvm_id)
			fd.write ( "true\n" )

	def change_possible(self, dom):
		generic.Device.change_possible(self, dom)
		if not self.template == util.get_attr(dom, "template", self.template):
			if self.topology.state == "started" or self.topology.state == "prepared":
				raise fault.new(fault.IMPOSSIBLE_TOPOLOGY_CHANGE, "Template of kvm %s cannot be changed" % self.name)
		if self.topology.state == "started":
			raise fault.new(fault.IMPOSSIBLE_TOPOLOGY_CHANGE, "Changes of running KVMs are not supported")

	def change_run(self, dom, task, fd):
		"""
		Adapt this device to the new device
		"""
		self.template = util.get_attr(dom, "template", self.template)
		ifaces=set()
		for x_iface in dom.getElementsByTagName("interface"):
			name = x_iface.getAttribute("id")
			ifaces.add(name)
			try:
				iface = self.interfaces_get(name)
			except generic.Interface.DoesNotExist:
				#new interface
				iface = generic.Interface()
				iface.init(self, x_iface)
				self.interfaces_add(iface)
				if self.topology.state == "prepared":
					iface_id = re.match("eth(\d+)", iface.name).group(1)
					fd.write("qm set %s --vlan%s e1000\n" % ( self.kvm_id, iface_id ) )
		for iface in self.interfaces_all():
			if not iface.name in ifaces:
				#deleted interface
				if self.topology.state == "prepared":
					iface_id = re.match("eth(\d+)", iface.name).group(1)
					#FIXME: find a way to delete interfaces
				iface.delete()
		

	def vnc_password(self):
		m = hashlib.md5()
		m.update(config.password_salt)
		m.update(str(self.name))
		m.update(str(self.kvm_id))
		m.update(str(self.vnc_port))
		m.update(str(self.topology.owner))
		return m.hexdigest()