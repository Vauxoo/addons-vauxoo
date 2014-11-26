# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: humberto@openerp.com.ve
#              angélicaisabelb@gmail.com
#              example of pycups-1.9.52
#    Planified by: Nhomar Hernande
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
import cups


def do_indent(indent):
    return "  " * indent


def getippqueue(dev, queue, depth):
  #  print "entro en el metodo: getippqueue"
    name = dev.rfind('/')
    name = dev[name + 1:]
    dev = dev[6:]
    e = dev.find(':')
    if e == -1:
        e = dev.find('/')
    host = dev[:e]
    cups.setServer(host)
    try:
        c = cups.Connection()
        printers = c.getPrinters()
    except RuntimeError:
        # Failed to connect.
        return
    except cups.IPPError, e:
        if e == cups.IPP_OPERATION_NOT_SUPPORTED:
            # CUPS-Get-Printers not supported so not a CUPS server.
            printers = {}
            classes = {}
        else:
            return
    try:
        queue = c.getPrinterAttributes(name)
    except cups.IPPError, e:
        # Failed to connect.
        return

    dev = queue['device-uri']
    getqueue(name, queue, host, depth + 1, printers, classes)


def getqueue(name, queue, host, depth, printers, classes):
    # print "entro en el metodo: getqueue"
    do_indent(depth)
    if queue['printer-type'] & cups.CUPS_PRINTER_CLASS:
       # print "%s* Name:\t%s[@%s] (class)" % (indent, name, host)
        dev = queue['device-uri']
        if dev.startswith('ipp:'):
            getippqueue(dev, queue, depth)
        else:
            members = classes[name]
            depth += 1
            do_indent(depth)
            for member in members:
                getqueue(member, printers[member], host,
                         depth, printers, classes)
    else:
       # print "%s* Name:\t%s[@%s]" % (indent, name, host)
        dev = queue['device-uri']
       # print "%sURI:\t%s" % (indent, dev)
       # print "%sInfo:\t%s" % (indent, info)
        if dev.startswith('ipp:'):
            getippqueue(dev, name, depth)


def gethost(host=None, depth=0):
   # print "entro aqui"
    if not host:
        host = "localhost"
    cups.setServer(host)
    c = cups.Connection()
    printers = c.getPrinters()
    do_indent(depth)
    lista_impresoras = []
    for name, queue in printers.iteritems():
        getqueue(name, queue, host, depth, printers, classes)
        lista_impresoras.append(name)
    return lista_impresoras
