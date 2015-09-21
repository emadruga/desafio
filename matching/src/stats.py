import sys,re,getopt
import unicodedata

def usage():
    print "stats.py [--input file] [--key_sorted|--value_sorted] [-k|-v]"
    
freq = dict()
filename = './planilhas/base-smartphone-marketplace-utf8.txt'
is_reverse_order = False
sort_order = "v"

try:
    opts, args = getopt.getopt(sys.argv[1:], "rhkvi:", ["help", "key_sorted","value_sorted","input="])
except getopt.GetoptError as err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

verbose = False
for o, a in opts:
    if o == "-r":
        is_reverse_order = True
    elif o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-k", "--key_sorted"):
        sort_order = "k"
    elif o in ("-v", "--value_sorted"):
        sort_order = "v"
    elif o in ("-i", "--input"):
        filename = a
    else:
        print "o: %s" % o
        assert False, "unhandled option"

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

if sort_order == "k":
    for prod, count in iter(sorted(freq.iteritems(), reverse = is_reverse_order)):
        print "%20s: %10d" % (prod,count)
else:
    for prod, count in iter(sorted(freq.iteritems(),
                                key=lambda x: x[1], reverse = is_reverse_order)):
        print "%20s: %10d" % (prod,count)
