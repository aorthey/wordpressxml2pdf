import xml.etree.ElementTree
from subprocess import call
from bs4 import BeautifulSoup
import re
import sys
import os.path
fname = 'motionplanning.wordpress.2016-12-22.xml'
basename = os.path.basename(fname)
basename = os.path.splitext(basename)
texname = basename[0]+'.tex'
pdfname = basename[0]+'.pdf'
trashnamelog = basename[0]+'.log'
trashnameaux = basename[0]+'.aux'

e = xml.etree.ElementTree.parse(fname)
root = e.getroot()

posts = []
for channel in root:
  print channel
  for post in channel.findall('item'):
    title = post.find('title')
    draftPaper=False
    if len(title.text) < 40:
      draftPaper = True
    for item in post.iter():
      if re.search('.+[^_]status',item.tag):
        if item.text=='draft':
          print 'delete '+item.text+' (title: '+title.text+')'
          draftPaper=True
                            
    if not draftPaper:
      post.title = title.text
      for item in post.iter():
        if re.search('.+content.+[^_]encoded',item.tag):
          if item.text:
            post.text = item.text
      posts.append(post)

#print "formatting to TeX"
#print "Obtained #"+str(len(posts))+" posts"

tex = open(texname,'w')

tex.write("\\documentclass[11pt]{article}\n")

tex.write("\\usepackage{amsmath}\n")
tex.write("\\begin{document}\n")
tex.write("\\tableofcontents\n")
tex.write("\\clearpage\n")
ictr = 0

## in reverse order
for post in reversed(posts):
  text = post.text
  title = post.title
  #recursive = re.compile(r'<.*?>')
  soup = BeautifulSoup(text,'lxml')
  #cleantext = recursive.sub('', text)

  text = text.replace("<em>","{\it{")
  text = text.replace("</em>","}}")
  text = re.sub(r"\$latex",r"$",text)
  text = re.sub(r'<a.*href=\"(.*)\".*>(.*)</a>',r'\2 (\1)\n',text)
  text = re.sub(r"\&nbsp;",r"",text)
  text = re.sub(r"\&gt;",r">",text)
  text = re.sub(r"_",r"\\_",text)
  #print text
  if re.search("<.*>(.*)<",text):
    reres = re.search("<.*>(.*)<.*>",text)
    print "FOUND UNMATCHED TAG"
    print reres.group(0)
    sys.exit(0)
  if re.search("\&",text):
    reres = re.search("\&.*;",text)
    print "FOUND UNMATCHED TAG"
    print reres.group(0)
    sys.exit(0)

  title = re.sub(r"_",r"\\_",title)

  ##prettify text
  tex.write("\\section{"+title+"}\n\n")
  tex.write(text+"\n\n")
tex.write("\\end{document}\n")

tex.close()
call(["rm", trashnamelog])
call(["rm", trashnameaux])
call(["pdflatex", texname])
print "Created tex file: ",texname
print "Created pdf file: ",pdfname
call(["apvlv", pdfname])
