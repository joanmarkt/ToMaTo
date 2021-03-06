# -*- coding: utf-8 -*-
# ToMaTo (Topology management software) 
# Copyright (C) 2010 Dennis Schwerdel, University of Kaiserslautern
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from tomato.auth import User

class Provider:
	def __init__(self, guest_user="guest", admin_user="admin"):
		self.guest_user = guest_user
		self.admin_user = admin_user
	
	def login(self, username, password): #@UnusedVariable, pylint: disable-msg=W0613
		if username==self.guest_user:
			return User(name=username, is_user=False)
		elif username==self.admin_user:
			return User(name=username, is_admin=True)
		else:
			return User(name=username)

def init(**kwargs):
	return Provider(**kwargs)