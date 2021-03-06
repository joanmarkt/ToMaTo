#!/usr/bin/python
# -*- coding: utf-8 -*-

def parseArgs():
	import argparse, getpass
	parser = argparse.ArgumentParser(description="ToMaTo XML-RPC Client", add_help=False)
	parser.add_argument('--help', action='help')
	parser.add_argument("--hostname" , "-h", required=True, help="the host of the server")
	parser.add_argument("--port", "-p", default=8000, help="the port of the server")
	parser.add_argument("--ssl", "-s", action="store_true", default=False, help="whether to use ssl")
	parser.add_argument("--username", "-U", help="the username to use for login")
	parser.add_argument("--password", "-P", help="the password to use for login")
	parser.add_argument("--file", "-f", help="a file to execute")
	parser.add_argument("arguments", nargs="*", help="python code to execute directly")
	options = parser.parse_args()
	if not options.username:
		options.username=raw_input("Username: ")
	if not options.password:
		options.password=getpass.getpass("Password: ")
	return options

class ServerProxy(object):
	def __init__(self, url, **kwargs):
		import xmlrpclib
		self._xmlrpc_server_proxy = xmlrpclib.ServerProxy(url, **kwargs)
	def __getattr__(self, name):
		call_proxy = getattr(self._xmlrpc_server_proxy, name)
		def _call(*args, **kwargs):
			return call_proxy(args, kwargs)
		return _call

def getConnection(hostname, port, ssl, username, password):
	return ServerProxy('%s://%s:%s@%s:%s' % ('https' if ssl else 'http', username, password, hostname, port), allow_none=True)
	
def runInteractive(locals):
	prompt = "ToMaTo"
	import readline, rlcompleter, code
	readline.parse_and_bind("tab: complete")
	readline.set_completer(rlcompleter.Completer(locals).complete)
	console = code.InteractiveConsole(locals)
	console.interact('Type "help()" or "help(method)" for more information.')
	
def runSource(locals, source):
	import code
	interpreter = code.InteractiveInterpreter(locals)
	interpreter.runsource(source)

def runFile(locals, file):
	import sys, os
	sys.path.insert(0, os.path.dirname(file))
	def shell():
		runInteractive(locals)
	locals["shell"] = shell
	__builtins__.__dict__.update(locals)
	locals["__name__"]="__main__"
	locals["__file__"]=file
	execfile(file, locals)
	sys.path.pop(0)

def getLocals(api):
	locals = {}
	def help(method=None):
		if method is None:
			print "Available methods:\tType help(method) for more infos."
			print ", ".join(api._listMethods())
		else:
			if not isinstance(method, str):
				method = filter(lambda name: locals[name] is method, locals)[0]
			print "Signature: " + api._methodSignature(method)
			print api._methodHelp(method)
	def load(file, name=None):
		import imp, os, sys
		files = filter(lambda dir: os.path.exists(os.path.join(dir, file)), sys.path)
		if files:
			file = os.path.join(files[0], file)
		if not name:
			name = os.path.basename(file)
		mod = imp.load_source(name, file)
		locals[name] = mod
		return mod
	locals.update(api=api, help=help, load=load)
	import xmlrpclib
	try:
		for func in api._listMethods():
			locals[func] = getattr(api, func)
	except xmlrpclib.ProtocolError, err:
		print "Protocol Error %s: %s" % (err.errcode, err.errmsg)
		import sys
		sys.exit(-1)
	return locals

def run():
	options = parseArgs()
	api = getConnection(options.hostname, options.port, options.ssl, options.username, options.password)
	locals = getLocals(api)
	if options.arguments:
		runSource(locals, options.arguments)
	elif options.file:
		runFile(locals, options.file)
	else:
		runInteractive(locals)
	
if __name__ == "__main__":
	run()