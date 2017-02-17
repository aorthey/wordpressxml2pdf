#!/usr/bin/python
import xml.etree.ElementTree
from subprocess import call
from bs4 import BeautifulSoup
import re
import sys
import os.path

if len(sys.argv) != 2:
  print "#"*80
  print "usage: wordpressxml2pdf [filename.xml]"
  print "#"*80
  print ""
  print "your input:"
  print sys.argv
  print "#"*80
  sys.exit(0)

fname = sys.argv[1]
basename = os.path.basename(fname)
basename = os.path.splitext(basename)
texname = basename[0]+'.tex'
pdfname = basename[0]+'.pdf'
trashnamelog = basename[0]+'.log'
trashnameaux = basename[0]+'.aux'

e = xml.etree.ElementTree.parse(fname)
root = e.getroot()

def DateToStr(date):
  m = re.match('^([A-Za-z,\t ]*)(?P<day>[0-9]?[0-9]).(?P<month>[A-Za-z]+).(?P<year>[0-9]+).*$',date)
  if m:
    dd= m.group('day')
    mmm= m.group('month')
    yyyy= m.group('year')
    dstr = dd + " " + mmm + " " + yyyy
    return dstr
  return None


def ExtractTag(itemtag):
  m = []
  m = re.match('^(?P<link>\{.*\})?(?P<tag>.*)$',itemtag)
  tag = m.group('tag')
  link = m.group('link')
  if link is not None:
    if re.search('content',link):
      tag = "content"+tag
  return tag

posts = []
for channel in root:
  for post in channel.findall('item'):

    validPost=True

    for item in post.iter():
      tag = ExtractTag(item.tag)
      if tag=='status':
        if item.text=='draft':
          title = post.find('title')
          print 'delete '+item.text+' (title: '+title.text+')'
          validPost = False
      if tag == 'contentencoded':
        if item.text is None:
          validPost = False
        
    if validPost:
      for item in post.iter():
        tag = ExtractTag(item.tag)
        #if re.search('.+content.+[^_]encoded',item.tag):
        if tag == 'title':
          post.title= item.text
        if tag == 'contentencoded':
          post.text = item.text
        if item.tag=='pubDate':
          post.date= DateToStr(item.text)
      posts.append(post)

#print "formatting to TeX"
#print "Obtained #"+str(len(posts))+" posts"

tex = open(texname,'w')

tex.write("\\documentclass[11pt]{article}\n")

tex.write("\\usepackage{amsmath}\n")
tex.write("\\usepackage{amsfonts}\n")
tex.write("\\setcounter{secnumdepth}{0}\n")
tex.write("\\begin{document}\n")
tex.write("\\begin{center}\n")
tex.write("{\\Huge Research Notebook}\\newline\\newline \n")
tex.write("\\end{center}\n")
tex.write("\\tableofcontents\n")
tex.write("\\clearpage\n")
ictr = 0

## in reverse order
for post in reversed(posts):
  text = post.text
  title = post.title
  date = post.date
  #recursive = re.compile(r'<.*?>')
  soup = BeautifulSoup(text,'lxml')
  #cleantext = recursive.sub('', text)

  text = re.sub(r'<p.*>(.*)',r'\1',text,re.DOTALL)
  text = re.sub(r'</p>',r'\n',text,re.DOTALL)
  text = re.sub(r"<em>",r"{\it{",text)
  text = re.sub(r"</em>",r"}}",text)
  text = re.sub(r"\$latex",r"$",text)
  text = re.sub(r'<a.*href=\"(.*)\".*>(.*)</a>',r'\2 (\1)\n',text)
  text = re.sub(r"\&nbsp;",r"",text)
  text = re.sub(r"\&gt;",r">",text)
  text = re.sub(r"\&lt;",r"<",text)
  text = re.sub(r"\&amp;",r"\&",text)
  text = re.sub(r"\&quot;",r"",text)
  text = re.sub(r"_",r"\\_",text)
  text = re.sub(r"<h3>(.*)(\n?)</h3>",r"\n{\\bf{\1}}\n\n",text)
  text = re.sub(r"<h4>(.*)</h4>",r"\n{\\bf{\1}}\n\n",text)
  text = re.sub(r"<h5>(.*)</h5>",r"\n{\\bf{\1}}\n\n",text)
  text = re.sub(r"<b>(.*)</b>",r"{\\bf{\1}}",text)
  text = re.sub(r"<strong>(.*)</strong>",r"{\\bf{\1}}",text)
  #print text
  if re.search("<.*>(.*)<",text):
    reres = re.search("<.*>(.*)<.*>",text)
    print "FOUND UNMATCHED TAG"
    print reres.group(0)
    sys.exit(0)
  if re.search("\&",text):
    reres = re.search("\&.*;",text)
    if reres:
      print "FOUND UNMATCHED CHAR"
      print reres.group(0)
      sys.exit(0)

  title = re.sub(r"_",r"\\_",title)

  ### clean up weird chars
  text = re.sub(ur'[\u00BF]',r'',text)
  ##prettify text
  sectitle="---Date:"+date+"---"
  tex.write("\\section*{"+sectitle+"}\\addcontentsline{toc}{section}{"+sectitle+"}\n\n")
  tex.write("\\subsection{ "+title+"}\n\n")
  tex.write(text+"\n\n")
tex.write("\\end{document}\n")

tex.close()
call(["rm", trashnamelog])
call(["rm", trashnameaux])
call(["pdflatex", texname])
call(["pdflatex", texname])
print "Created tex file: ",texname
print "Created pdf file: ",pdfname
call(["apvlv", pdfname])
