from lxml import etree
import sys

xmlfile = sys.argv[1]
parser = etree.XMLParser(load_dtd=True,no_network=False)
tree = etree.parse(xmlfile, parser=parser)
