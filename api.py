#! /usr/bin/env python  
# -*- coding: utf-8 -*-

from xml.dom.minidom import Document

class xmlbuilder:
    
    def __init__(self, root):
        self.doc = Document()
        self.root = self.doc.createElement(root)
        self.doc.appendChild(self.root)

    def node(self, key, val=None):
        item = self.doc.createElement(key);
        if val is not None:
            item_val = self.doc.createTextNode(val.encode("utf-8"))
            item.appendChild(item_val)
        return item

    def append(self, child=None, root=None):
        if root is None and child is not None:
            self.root.appendChild(child)
        elif child is not None:
            root.appendChild(child)
            
    def toprettyxml(self,indent="    "):
        return self.doc.toprettyxml(indent)
#<root>
#<isChanged>true</isChanged>
#<config>
#    <version_id>20110901010101</version_id>
#    <threshold>
#        <threshold_mainland>3500</threshold_mainland>
#        <threshold_foreign>4800</threshold_foreign>
#    </threshold>
#    <taxrate>
#        ((0, 0.03, 0),
#        (1500, 0.10, 105),
#        (4500, 0.20, 555),
#        (9000, 0.25, 1055),
#        (35000, 0.30, 2755),
#        (55000, 0.35, 5505),
#        (80000, 0.45, 13505))
#    </taxrate>
#</config>
#</root>
def genTestXml():
    xml = xmlbuilder('root')
    xml.append(xml.node('isChanged','false'))
    config = xml.node('config')
    version_id = xml.node('version_id', '20110901010101')
    
    threshold  = xml.node('threshold')
    threshold.appendChild(xml.node('threshold_mainland','3500'))
    threshold.appendChild(xml.node('threshold_foreign','4800'))
    
    taxrate = xml.node('taxrate','((0, 0.03, 0),(1500, 0.10, 105),(4500, 0.20, 555),(9000, 0.25, 1055),(35000, 0.30, 2755),(55000, 0.35, 5505),(80000, 0.45, 13505))')
    config.appendChild(version_id)
    config.appendChild(threshold)
    config.appendChild(taxrate)
    
    xml.append(config)

    return xml.toprettyxml()


print genTestXml()