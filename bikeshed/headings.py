# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals
from .messages import *
from .htmlhelpers import *
from .config import simplifyText

def processHeadings(doc, scope="doc"):
    # scope arg can be "doc" or "all"
    # "doc" ignores things that are part of boilerplate
    for el in findAll('h2, h3, h4, h5, h6', doc):
        addClass(el, 'heading')
    headings = []
    for el in findAll(".heading:not(.settled)", doc):
        if scope == "doc" and treeAttr(el, "boilerplate"):
            continue
        headings.append(el)
    resetHeadings(doc, headings)
    determineHeadingLevels(doc, headings)
    addHeadingIds(doc, headings)
    addHeadingAlgorithms(doc, headings)
    dedupIds(doc, headings)
    addHeadingBonuses(doc, headings)
    for el in headings:
        addClass(el, 'settled')
    if scope == "all" and doc.md.groupIsW3C:
        checkPrivacySecurityHeadings(findAll(".heading", doc))

def resetHeadings(doc, headings):
    for header in headings:
        # Reset to base, if this is a re-run
        if find(".content", header) is not None:
            content = find(".content", header)
            moveContents(header, content)

        # Insert current header contents into a <span class='content'>
        content = E.span({"class":"content"})
        moveContents(content, header)
        appendChild(header, content)

def addHeadingIds(doc, headings):
    neededIds = set()
    hadSecurity = False
    hadPrivacy = False
    for header in headings:
        if header.get('id') is None:
            if header.get("data-dfn-type") is None:
                # dfn headings will get their IDs assigned by the dfn code
                neededIds.add(header)
                header.set('id', simplifyText(textContent(find(".content", header))))
        if header.get("oldids"):
            oldIDs = [h.strip() for h in header.get("oldids").strip().split(",")]
            for oldID in oldIDs:
                appendChild(header, E.span({"id":oldID}))
    if len(neededIds) > 0:
        warn("You should manually provide IDs for your headings:\n{0}",
            "\n".join("  "+outerHTML(el) for el in neededIds))

def checkPrivacySecurityHeadings(headings):
    security = False
    privacy = False
    for header in headings:
        text = simplifyText(textContent(find(".content", header)))
        if text == "security-considerations":
            security = True
        if text == "privacy-considerations":
            privacy = True
    if not security and not privacy:
        warn("This specification has neither a 'Security Considerations' nor a 'Privacy Considerations' section. Please consider adding both.")
    elif not security:
        warn("This specification does not have a 'Security Considerations' section. Please consider adding one.")
    elif not privacy:
        warn("This specification does not have a 'Privacy Considerations' section. Please consider adding one.")

def addHeadingAlgorithms(doc, headings):
    for header in headings:
        if header.get('data-algorithm') == "":
            header.set('data-algorithm', textContent(header).strip())

def determineHeadingLevels(doc, headings):
    headerLevel = [0,0,0,0,0]
    def incrementLevel(level):
        headerLevel[level-2] += 1
        for i in range(level-1, 5):
            headerLevel[i] = 0
    def printLevel():
        return '.'.join(unicode(x) for x in headerLevel if x > 0)

    skipLevel = float('inf')
    for header in headings:
        # Add the heading number.
        level = int(header.tag[-1])

        # Reset, if this is a re-run.
        if(header.get('data-level')):
            del header.attrib['data-level']

        # If we encounter a no-num, don't number it or any in the same section.
        if hasClass(header, "no-num"):
            skipLevel = min(level, skipLevel)
            continue
        if skipLevel < level:
            continue
        else:
            skipLevel = float('inf')

        incrementLevel(level)
        header.set('data-level', printLevel())

def addHeadingBonuses(doc, headings):
    for header in headings:
        if header.get("data-level") is not None:
            secno = E.span({"class":"secno"}, header.get('data-level') + '. ')
            header.insert(0, secno)
