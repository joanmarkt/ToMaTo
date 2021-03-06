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

from django.db import models
import xmlrpclib, traceback

class Error(models.Model):
	date = models.DateTimeField(auto_now_add=True)
	title = models.CharField(max_length=255)
	message = models.TextField(blank=True)
	
	def toDict(self):
		return {"id": self.id, "date": self.date, "title": self.title, "message": self.message} # pylint: disable-msg=E1101

def errors_all():
	return Error.objects.all() # pylint: disable-msg=E1101

def errors_add(title, message):
	Error.objects.create(title=title, message=message) # pylint: disable-msg=E1101

def errors_remove(error_id):
	if not error_id:
		Error.objects.all().delete()
	else:
		Error.objects.get(id=error_id).delete() # pylint: disable-msg=E1101

class Fault(xmlrpclib.Fault):
	def __str__ (self):
		return "Error %s: %s" % (self.faultCode, self.faultString)

UNKNOWN_ERROR = -1
AUTHENTICATION_ERROR = 300
USER_ERROR = 400
INTERNAL_ERROR = 500

def _must_log(exc):
	if isinstance(exc, Fault):
		return exc.faultCode != USER_ERROR
	return True 

def log(exc):
	if _must_log(exc):
		traceback.print_exc(exc)
		errors_add('%s:%s' % (exc.__class__.__name__, exc), traceback.format_exc(exc))

def wrap(exc):
	if isinstance(exc, Fault):
		return exc
	return new('%s:%s' % (exc.__class__.__name__, exc))

def new(text, code=UNKNOWN_ERROR):
	return Fault(code, text)

def check(condition, errorStr, formatOpt = None, code=USER_ERROR):
	if not condition:
		if formatOpt:
			errorStr = errorStr % formatOpt
		raise new(errorStr, code)

