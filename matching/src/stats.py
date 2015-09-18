import sys,re
import unicodedata

freq = dict()

filename = './planilhas/base-smartphone-marketplace-utf8.txt'
if len(sys.argv) > 1:
    filename = sys.argv[1]

with open(filename) as fp:
    for line in fp:
        #remove accents - input to normalize must be unicode
        unicode_line  = line.decode('utf8')
        nfkd_line     = unicodedata.normalize('NFKD',unicode_line.lower())
        ascii_line    = nfkd_line.encode('ASCII', 'ignore')

        words = re.split(r'\s', ascii_line)

        if words and words[0]:
            if words[0] in freq:
                freq[words[0]] +=1
            else:
                freq[words[0]] = 1

for prod, count in iter(sorted(freq.iteritems(),
                               key=lambda x: x[1], reverse = True)):
    print "%20s: %10d" % (prod,count)
