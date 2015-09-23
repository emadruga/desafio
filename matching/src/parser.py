import sys
import unicodedata

sys.path.insert(0,"../..")

if sys.version_info[0] >= 3:
    raw_input = input

import ply.lex as lex
import ply.yacc as yacc
import os


class Attribute(object):
    def __init__(self, type, value):
        self.type  = type
        self.value = value
    def __repr__(self):
        return "a(%r, %r)" % (self.type, self.value)

    
class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = { }
        self.filename = kw.get('filename',0)
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
        
    def processList(self, list):
        for attrib in list:
            print attrib
            
    def run(self):
        attribList = None
        with open(self.filename) as fp:
            for line in fp:
                line.rstrip('\n')
                #remove accents - input to normalize must be unicode
                unicode_line  = line.decode('utf8')
                nfkd_line     = unicodedata.normalize('NFKD',unicode_line)
                ascii_line    = nfkd_line.encode('ASCII', 'ignore')
                print "------------------"
                print "%s" % line
                try:
                    attribList = yacc.parse(ascii_line.lower())
                    #self.processList (attribList)
                    print attribList
                    
                except TypeError as e:
                    print ">>> %s" % e
                except SyntaxError as e:
                    print ">>> %s" % e


class ProductParser(Parser):
    tokens = (
        'BRAND','PRODUCT','TECHNOLOGY', 'COLOR','NUMCHIP',
        'ATTRIB','NUMBER','FLOAT','SEP', 'UNLOCKED','GIGABYTES',
        'MEGAPIXELS', 'MP3','INCHES','PROVIDER','OS_NAME',
        'COMMON_MODEL_SAMSUNG',
        'COMMON_MODEL_SONY',
        'COMMON_MODEL_MOTOROLA',
        ) 

    # Tokens
    
    t_SEP          = r'[\-\,\/\|\:\.\+]' 
    t_INCHES       = r'[\"]' 
    t_GIGABYTES    = r'gb\b' 
    t_ATTRIB       = r'[a-zA-Z_][a-zA-Z0-9_]*'
    
    def t_COLOR(self,t):
        r'azul|branco|preto|dourado|titanio|verde|grafite|vermelho|rosa'
        return t

    def t_UNLOCKED(self,t):
        r'desbloqueado'
        return t

    def t_TECHNOLOGY(self,t):
        r'3g|4g'
        return t

    def t_MEGAPIXELS(self,t):
        r'mp|megapixels'
        return t

    def t_MP3(self,t):
        r'mp3|mp3\s+player'
        return t

    def t_PROVIDER(self,t):
        r'\bclaro\b|\boi\b|\btim\b|\bvivo\b'
        return t

    
    def t_NUMCHIP(self,t):
        r'dual\s+chip|tri\s+chip|quad\s+chip'
        return t

    def t_OS_NAME(self,t):
        r'android|windows\s+phone|windows'
        return t

    def t_COMMON_MODEL_SAMSUNG(self,t):
        r'galaxy'
        return t

    def t_COMMON_MODEL_SONY(self,t):
         r'xperia'
         return t
        
    def t_COMMON_MODEL_MOTOROLA(self,t):
         r'moto\b'
         return t

    def t_PRODUCT(self,t):
        r'smartphone|smart\s+tv|capa|viva[\-\s]voz|suporte|pen[ \-]drive|celular|controle|camera|fone|kit|monofone|carregador|bracadeira|joystick|cabo|bastao'
        return t
    
    def t_BRAND(self,t):
        r'samsung|huawei|nokia|lg|sony\s+ericsson|positivo|sony|microsoft|motorola|asus|alcatel|multilaser|\bblu\b'
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
        t.lexer.skip(1)
        raise TypeError ("Illegal character '%s'" % t.value[0])

    # Parsing rules
    # precedence = (
    #     ('left','PLUS','MINUS'),
    #     ('left','TIMES','DIVIDE'),
    #     ('left', 'EXP'),
    #     ('right','UMINUS'),
    #     )

    def p_statement(self, p):
        'statement : PRODUCT  product_prefix_list product_id attribute_list'
        p[0] = [ Attribute('product', p[1]) ] 
        if isinstance(p[2],(list,tuple)) and len(p[2]) > 0:
            p[0] = p[0] + p[2]
        if isinstance(p[3],(list,tuple)) and len(p[3]) > 0:
            p[0] = p[0] + p[3]
        if isinstance(p[4],(list,tuple)) and len(p[4]) > 0:
            p[0] = p[0] + p[4]

    def p_product_prefix_list(self, p):
        """
        product_prefix_list :  product_prefix_list product_prefix
                            |  product_prefix
                            |
        """
        if len(p) == 2:
            if len([ p[1] ]) > 0:
                p[0] = [ p[1] ]
        elif  len(p) == 3:
            p[0] = p[1] 
            if len([ p[2] ]) > 0:
                p[0] += [ p[2] ]

    def p_product_prefix_unlocked(self, p):
        """
        product_prefix : UNLOCKED           
        """
        p[0] = Attribute('unlocked', 1)

        
    def p_product_prefix_numchip(self, p):
        """
        product_prefix : NUMCHIP           
        """
        p[0] = Attribute('numchip', p[1])

    def p_product_prefix_provider(self, p):
        """
        product_prefix : PROVIDER          
        """
        p[0] = Attribute('provider', p[1])

    def p_product_id(self, p):
        """
        product_id : BRAND ATTRIB attribute_list
                   
        """
        p[0] = [
            Attribute('brand', p[1]),
            Attribute('model', p[2]),
        ] 
        if isinstance(p[3],(list,tuple)) and len(p[3]) > 0:
            p[0] += p[3]
            
    def p_product_id_common_models(self, p):
        """
        product_id :   BRAND common_models attribute_list
                   |   common_models attribute_list
        """
        if len(p) == 3:
            p[0] = p[1]
            if isinstance(p[2],(list,tuple)) and len(p[2]) > 0:
                p[0] += p[2]
        elif len(p) == 4:
            p[0] = p[2]
            if isinstance(p[3],(list,tuple)) and len(p[3]) > 0:
                p[0] += p[3]

    def p_common_models_samsung(self, p):
        """
        common_models : COMMON_MODEL_SAMSUNG
        """
        p[0] =  [ Attribute('brand', 'samsung'), Attribute('model', p[1]) ]

    def p_common_models_sony(self, p):
        """
        common_models : COMMON_MODEL_SONY
        """
        p[0] =  [ Attribute('brand', 'sony'), Attribute('model', p[1]) ]

    def p_common_models_motorola(self, p):
        """
        common_models : COMMON_MODEL_MOTOROLA
        """
        p[0] =  [ Attribute('brand', 'motorola'), Attribute('model', p[1]) ]

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

    def p_attribute_screen_diagonal(self, p):
        """
        attribute    : NUMBER INCHES
                     | FLOAT  INCHES
        """
        p[0] = Attribute('screen_diagonal', p[1])
        
    def p_attribute_camera_resolution(self, p):
        """
        camera_resolution : NUMBER MEGAPIXELS
                          | FLOAT  MEGAPIXELS
        """
        p[0] = Attribute('camera_resolution', p[1])

    def p_attribute_operating_system(self, p):
        """
        attribute  : OS_NAME NUMBER
                   | OS_NAME FLOAT
        """
        p[0] = Attribute('operating_system', p[1])

    def p_attribute_storage(self, p):
        """
        attribute  :  NUMBER GIGABYTES
                   |  FLOAT GIGABYTES
        """
        p[0] = Attribute('storage', p[1])

    def p_attribute_provider(self, p):
        """
        attribute : PROVIDER          
        """
        p[0] = Attribute('provider', p[1])

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
        attribute : UNLOCKED
        """
        p[0] = Attribute('unlocked', 1)

    def p_attribute_mp3_player(self, p):
        """
        attribute : MP3
        """
        p[0] = Attribute('mp3_player', 1)

    def p_attribute_common_models(self, p):
        """
        attribute : COMMON_MODEL_SAMSUNG
                  | COMMON_MODEL_SONY
                  | COMMON_MODEL_MOTOROLA
        """
        p[0] = Attribute('model', p[1])
    
    def p_attribute_brand(self, p):
        """
        attribute : BRAND
        """
        p[0] = Attribute('brand', p[1])

    def p_attribute_product(self, p):
        """
        attribute : PRODUCT
        """
        p[0] = Attribute('product', p[1])

    def p_error(self, p):
        if p:
            raise SyntaxError ("Syntax error at '%s'" % p.value)
        else:
            raise SyntaxError ("Syntax error at EOF")

if __name__ == '__main__':

    file = './planilhas/sample-utf8.txt'
    if len(sys.argv) > 1:
        file = sys.argv[1]
    prod = ProductParser(debug = 0, filename = file)
    prod.run()
    
