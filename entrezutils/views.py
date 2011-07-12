import urllib
from xml.dom.minidom import parseString
from xml.dom.minidom import Node

from django.http import HttpResponse

import models

##obsolete- moved to entrezutils/models-- use those adapters instead

# def evalSingle(node, withName=True, children=True):
#     if node.tagName == "Item":
#         tagName = node.getAttribute("Name")
#     else:
#         tagName = node.tagName
#     if children:
#         if withName:
#             return "%s:'%s'" % (tagName, node.childNodes[0].nodeValue)
#         else:
#             return "'%s'" % node.childNodes[0].nodeValue
#     else:
#         return "%s: null" % tagName

# def xmlToJSON(node):
#     """Returns the JSON represenation of the entrez xml tree.
#     IF nodename is:
#        item and type list --> {name: [ xmlToJSON(dom.childNodes)]}
#        if childNodes.length == 0/1 {name: 'value'}
#        else {name: {childName: 'childValue' for all children}}
    
#     NOTE: the DTD is usually given, e.g.
#     http://www.ncbi.nlm.nih.gov/entrez/query/DTD/eSummary_041029.dtd
#     it would be COOL if we could automatically generate this fn using the DTD
#     """

#     if node.nodeType == Node.ELEMENT_NODE: #A new record
#         if node.hasChildNodes():
#             if len(node.childNodes) == 1 and \
#                node.childNodes[0].nodeType == Node.TEXT_NODE:
#                 return evalSingle(node)
#             elif node.tagName == "Item" and \
#                      node.getAttribute("Type") == "List":
#                 ls = [evalSingle(c, False) for c in node.childNodes]
#                 #print "LS %s " % ls
#                 return "%s:[%s]" % (node.getAttribute("Name"), ", ".join(ls))
#             else:
#                 rec = [xmlToJSON(c) for c in node.childNodes]
#                 #print "REC %s" % rec
#                 return "%s:{%s}" % (node.tagName, ", ".join(rec))

#         else:
#             return evalSingle(node, True, False)
    

# def remove_whitespace_nodes(node, unlink=False):
#     """
#     ref: http://code.activestate.com/recipes/303061-remove-whitespace-only-text-nodes-from-an-xml-dom/
#     Removes all of the whitespace-only text decendants of a DOM node.
    
#     When creating a DOM from an XML source, XML parsers are required to
#     consider several conditions when deciding whether to include
#     whitespace-only text nodes. This function ignores all of those
#     conditions and removes all whitespace-only text decendants of the
#     specified node. If the unlink flag is specified, the removed text
#     nodes are unlinked so that their storage can be reclaimed. If the
#     specified node is a whitespace-only text node then it is left
#     unmodified."""
    
#     remove_list = []
#     for child in node.childNodes:
#         if child.nodeType == Node.TEXT_NODE and \
#                not child.nodeValue.strip():
#             remove_list.append(child)
#         elif child.hasChildNodes():
#             remove_whitespace_nodes(child, unlink)
#     for node in remove_list:
#         node.parentNode.removeChild(node)
#         if unlink:
#             node.unlink()
                    
# def query(request, tool):
#     """This fn tries to call the entrez.eutil tool (e.g. esummary) with the
#     given parameters; receives the HTTP (XML) response from the entrez servers;
#     returns the XML response as JSON"""
#     params = "&".join(["%s=%s" % (k, request.GET[k]) \
#                        for k in request.GET.keys()])
    
#     URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/%s.fcgi?%s" % (tool, params)
#     #print URL
#     f = urllib.urlopen(URL)
#     tmp = f.read()
#     #print tmp
#     dom = parseString(tmp)
#     f.close()
#     #print dom.toprettyxml()
#     remove_whitespace_nodes(dom.documentElement)
    
#     return HttpResponse("{%s}" % xmlToJSON(dom.documentElement))

def GetPubmedArticle(request):
    """Tries to retrieve the pubmed summary information"""
    if request.GET['id']:
        tmp = models.PubmedArticle(request.GET['id'])
        return HttpResponse(tmp.to_json())
    else:
        return HttpResponse("{'success':false, 'err':'No PMID given!'}")
