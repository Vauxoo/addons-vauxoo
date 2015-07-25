# -*- encoding: utf-8 -*-
# import the os module, for the os.walk function
import os
import io


def write_version(pathdescriptor):
    with open(pathdescriptor, "rt") as filedescriptor:
        ddescriptor = filedescriptor.read()
        filedescriptor.close()
    desc = eval(ddescriptor)
    version = desc.get('version', 'No Version Found') or '0.1'
    ddescriptor2 = ddescriptor.replace(
        version, '%s.%s' % (version.split('.')[0], '5'))
    print('New Version %s' % eval(ddescriptor2).get('version', 'Problem'))
    with open(pathdescriptor, "wt") as filedescriptor2:
        filedescriptor2.write(ddescriptor2)
        filedescriptor2.close()
    return True

# Set the directory you want to start from
rootDir = '.'
modules = []
for dirName, subdirList, fileList in os.walk(rootDir):
    for fname in fileList:
        if fname == '__openerp__.py':
            modules.append(dirName)
            pdescriptor = os.path.join(dirName, fname)
            print(pdescriptor)
            fdescriptor = open(pdescriptor, 'r')
            ddescriptor = fdescriptor.read()
            descriptor = eval(ddescriptor)
            version = descriptor.get('version', 'No Version Found')
            print('Version %s for \t%s' % (version, dirName))
            write_version(pdescriptor)
            # All will be 3.0 on this release then I will increase 1 by one for
            # V8.0

print('Found %s modules' % len(modules))
