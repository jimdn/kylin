# -*- coding: utf-8 -*-
'''
	@author: 	jemuelmiao
	@filename: 	build.py
	@create: 	2019-03-02 13:25:20
	@modify:	2020-09-23 11:29:23
	@desc:		
'''
import os
import sys
import xml.etree.ElementTree as ET

PAGE_COUNT = 10
CMD_ALL = 'ALL'
gModules = []


class Getch():
	def __init__(self):
		try:
			self.impl = GetchWindows()
		except ImportError:
			self.impl = GetchUnix()

	def __call__(self):
		return self.impl()

class GetchWindows():
	def __init__(self):
		import msvcrt

	def __call__(self):
		import msvcrt
		return msvcrt.getch()

class GetchUnix():
	def __init__(self):
		import tty, termios

	def __call__(self):
		import tty, termios
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch


def getModules(path):
	moduleList = []
	tree = ET.parse(path)
	root = tree.getroot()
	for child in root.getchildren():
		if child.tag.endswith('modules'):
			for module in child.getchildren():
				moduleList.append(module.text)
	return moduleList

def visitDir(path, baseModule):
	if not os.path.isdir(path):
		print 'ERROR: Invalid Path[ %s ]!!!'%(path)
		sys.exit(1)
	for filename in os.listdir(path):
		pathname = os.path.join(path, filename)
		if os.path.isfile(pathname) and filename == 'pom.xml':
			modules = getModules(pathname)
			if len(modules) == 0:
				gModules.append(baseModule)
			else:
				for module in modules:
					if baseModule == '':
						visitDir(os.path.join(path, module), module)
					else:
						visitDir(os.path.join(path, module), baseModule + '/' + module)

def findSameModule(name):
	fitList = []
	for module in gModules:
		if module == name:
			return [module]
		elif module.find(name) != -1:
			fitList.append(module)
	return fitList

if __name__ == '__main__':
	# print os.path.dirname(os.path.realpath(__file__))
	visitDir(os.path.dirname(os.path.realpath(__file__)), '')
	name = ''
	moduleList = []
	getch = Getch()
	while True:
		name = raw_input(">>Input module name(Enter for all):")
		if name == '':
			moduleList = [CMD_ALL]
			break
			# print '>>Invalid module name!!!'
			# continue
		# elif name == CMD_ALL:
		# 	moduleList = [name]
		# 	break
		moduleList = findSameModule(name)
		if len(moduleList) == 1:
			break
		if len(moduleList) == 0:
			print '>>Module not find!!!'
			continue
		if len(moduleList) >= PAGE_COUNT:
			print '>>Too many modules(%d), press <space> see more!!!'%(len(moduleList))
		else:
			print '>>Too many modules(%d)!!!'%(len(moduleList))
		while len(moduleList) > 0:
			for i in xrange(min(PAGE_COUNT, len(moduleList))):
				print '\t' + moduleList[i]
			print ''
			moduleList = moduleList[PAGE_COUNT:]
			if len(moduleList) > 0 and ord(getch()) == 32:
				continue
			else:
				break
	print '>>Build module "%s" ?[Y/N]' % (moduleList[0]),
	while True:
		confirm = getch()
		if confirm in ['Y', 'y']:
			print ''
			if moduleList[0] == CMD_ALL:
				cmd = 'mvn clean package -DskipTests -T 8.0C'
			else:
				cmd = 'mvn clean package -DskipTests -e -T 8.0C -pl %s -am' % (moduleList[0])
			os.system(cmd)
			break
		elif confirm in ['N', 'n']:
			break
		else:
			continue
