import sys
import unicodedata

sys.path.insert(0,"../..")

if sys.version_info[0] >= 3:
    raw_input = input

import ply.lex as lex
import ply.yacc as yacc
import os

class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = { }
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
        except:
            modname = "parser"+"_"+self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"
        #print self.debugfile, self.tabmodule

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

    def run(self):
        attribList = None
        with open('./planilhas/sample-utf8.txt') as fp:
            for line in fp:
                #remove accents - input to normalize must be unicode
                unicode_line  = line.decode('utf8')
                nfkd_line     = unicodedata.normalize('NFKD',unicode_line)
                ascii_line    = nfkd_line.encode('ASCII', 'ignore')
                print "\n%r" % line
                attribList = yacc.parse(ascii_line.lower())
                print attribList

class Attribute(object):
    def __init__(self, type, value):
        self.type  = type
        self.value = value
    def __repr__(self):
        return "a(%r, %r)" % (self.type, self.value)
                
class ProductParser(Parser):
    tokens = (
        'BRAND','PRODUCT','TECHNOLOGY', 'COLOR','NUMCHIP',
        'ATTRIB','NUMBER','FLOAT','SEP','NAME', 'LOCK',
        'MEGAPIXELS',
        ) 

    # Tokens

    t_SEP          = r'[\-\,\/]' 
    t_NAME         = r'[a-zA-Z]+'
    t_ATTRIB       = r'[a-zA-Z_][a-zA-Z0-9_]*'
    t_MEGAPIXELS   = r'mp'
    
    def t_COLOR(self,t):
        r'azul|branco|preto|dourado|titanio|verde|vermelho|rosa'
        return t

    def t_LOCK(self,t):
        r'desbloqueado'
        return t

    def t_TECHNOLOGY(self,t):
        r'3g|4g'
        return t

    def t_NUMCHIP(self,t):
        r'dual\s+chip|tri\s+chip|quad\s+chip'
        return t
    
    def t_PRODUCT(self,t):
        r'smartphone|smart\s+tv|capa\s+protetora|viva[\-\s]voz'
        return t
    
    def t_BRAND(self,t):
        r'samsung|nokia|lg|sony\s+ericsson|sony|microsoft'
        return t

    def t_FLOAT(self, t):
        r'\d+[\.\,\-]\d+'
        return t
        
    def t_NUMBER(self, t):
        r'\d+'
        return t

    t_ignore = " \t"

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
    
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Parsing rules

    # precedence = (
    #     ('left','PLUS','MINUS'),
    #     ('left','TIMES','DIVIDE'),
    #     ('left', 'EXP'),
    #     ('right','UMINUS'),
    #     )

    def p_statement(self, p):
        'statement : PRODUCT product_id attribute_list'
        #  "Product: %s" % p[1]
        p[0] = [ Attribute('product', p[1]) ] 
        if isinstance(p[2],(list,tuple)) and len(p[2]) > 0:
            p[0] = p[0] + p[2]
        if isinstance(p[3],(list,tuple)) and len(p[3]) > 0:
            p[0] = p[0] + p[3]

    def p_product_id(self, p):
        """
        product_id : BRAND ATTRIB ATTRIB attribute_list
                   |
        """
        if len(p) == 5:
            myId = "%s %s" % (p[2],p[3])
            p[0] = [
                     Attribute('brand', p[1]),
                     Attribute('model', p[2]),
                     Attribute('model_number', p[3]),
            ] 
            if isinstance(p[4],(list,tuple)) and len(p[4]) > 0:
                p[0] += p[4]


    def p_attribute_list(self, p):
        """
        attribute_list : attribute_list attribute
                       | attribute_list SEP attribute
                       | attribute
        """
        if len(p) == 2:
            if len([ p[1] ]) > 0:
                p[0] = [ p[1] ]
        elif  len(p) == 3:
            p[0] = p[1] 
            if len([ p[2] ]) > 0:
                p[0] += [ p[2] ]
        elif  len(p) == 4:
            p[0] = p[1] 
            if len([ p[3] ]) > 0:
                p[0] += [ p[3] ]

    def p_attribute_empty(self, p):
        """
        attribute : empty
        """
        p[0] = [ ]

    def p_empty(self,p):
        'empty :'
        pass
    
    def p_attribute_name(self, p):
        """
        attribute : ATTRIB
        """
        p[0] = Attribute('generic', p[1])

        
    def p_attribute_number_rep(self, p):
        """
        attribute : NUMBER
                  | FLOAT
        """
        p[0] = Attribute('generic_num', p[1])

    def p_attribute_camera(self, p):
        """
        attribute : camera_resolution
        """
        p[0] = p[1]

    def p_attribute_camera_resolution(self, p):
        """
        camera_resolution : NUMBER MEGAPIXELS
                          | FLOAT  MEGAPIXELS
        """
        p[0] = Attribute('camera_resolution', p[1])

    def p_attribute_tech(self, p):
        """
        attribute : TECHNOLOGY
        """
        p[0] = Attribute('technology', p[1])

    def p_attribute_numchip(self, p):
        """
        attribute : NUMCHIP
        """
        p[0] = Attribute('numchip', p[1])

    def p_attribute_color(self, p):
        """
        attribute : COLOR
        """
        p[0] = Attribute('color', p[1])

    def p_attribute_lock(self, p):
        """
        attribute : LOCK
        """
        p[0] = Attribute('lock', 1)
        
        
    def p_attribute_brand(self, p):
        """
        attribute : BRAND
        """
        p[0] = Attribute('brand', p[1])

    # def p_attribute_product(self, p):
    #     """
    #     attribute : PRODUCT
    #     """
    #     print "Product: %s" % p[1]

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

if __name__ == '__main__':
    prod = ProductParser(debug = 0)
    prod.run()
    
