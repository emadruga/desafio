import sys,re
import ply.lex as lex
import ply.yacc as yacc

from myParser import Product,ProductAttribute,Parser,ParserException
                                
class MatchingParser(Parser):
    tokens = (
        'BRAND','PRODUCT','TECHNOLOGY', 'COLOR','NUMCHIP',
        'ATTRIB','NUMBER','FLOAT','SEP', 'UNLOCKED','GIGABYTES',
        'MP', 'MP3','INCHES','PROVIDER','OS_NAME',
        'COMMON_PRODUCT_LINE_SAMSUNG','SMARTPHONE',
        'COMMON_PRODUCT_LINE_SONY','GENERATION', 'ORDINAL',
        'COMMON_PRODUCT_LINE_MOTOROLA','LPAREN','RPAREN',
        ) 

    # Tokens
    t_LPAREN	   = r'\('
    t_RPAREN	   = r'\)'
    t_SEP          = r'[\-\,\/\|\:\.\+]' 
    t_INCHES       = r'[\"]|\'[\s]?\'' 
    t_ATTRIB       = r'[a-zA-Z_][a-zA-Z0-9_]*'
    
    def t_COLOR(self,t):
        r'azul|branco|preto|dourado|titanio|verde|grafite|vermelho|rosa'
        return t

    def t_UNLOCKED(self,t):
        r'desbloqueado'
        return t

    def t_ORDINAL(self,t):
        r'a\b'
        return t

    def t_TECHNOLOGY(self,t):
        r'3g|4g'
        return t

    def t_GIGABYTES(self,t):
        r'gb\b'
        return t

    def t_MP(self,t):
        r'mp'
        return t

    def t_MP3(self,t):
        r'mp3|mp3\s+player'
        return t

    def t_PROVIDER(self,t):
        r'\bclaro\b|\boi\b|\btim\b|\bvivo\b'
        return t

    def t_GENERATION(self,t):
        r'geracao[.]?'
        return t
    
    def t_NUMCHIP(self,t):
        r'dual\s+chip|tri\s+chip|quad\s+chip'
        return t

    def t_OS_NAME(self,t):
        r'android|ios|windows\s+phone|windows'
        return t

    def t_COMMON_PRODUCT_LINE_SAMSUNG(self,t):
        r'galaxy'
        return t

    def t_COMMON_PRODUCT_LINE_SONY(self,t):
         r'xperia'
         return t
        
    def t_COMMON_PRODUCT_LINE_MOTOROLA(self,t):
         r'moto\s+g|moto\s+maxx|moto\b'
         return t

    def t_SMARTPHONE(self,t):
         r'celular[\s\/]+smartphone|smartphone\b'
         return t

    def t_PRODUCT(self,t):
        r'smart\s+tv|console|smartphone|caixa|lavadora|projetor|sistema|ultrabook|xbox|game|notebook|dvd|tv\s+led|livro|kit|gopro|tablet'
        return t
    
    def t_BRAND(self,t):
        r'samsung|huawei|apple|nokia|lg|sony\s+ericsson|blackberry|positivo|sony|microsoft|motorola|asus|alcatel|multilaser|\bblu\b'
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
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)
        #raise ParserException (type    = 'Lexical Exception',
        #                       message ="Illegal character '%s'" % t.value[0])

    # Parsing rules
    # precedence = (
    #     ('left','PLUS','MINUS'),
    #     ('left','TIMES','DIVIDE'),
    #     ('left', 'EXP'),
    #     ('right','UMINUS'),
    #     )

    def p_all_products(self, p):
        """
        product_list : product_list product
                     | product
                     |
        """
        if len(p) == 3:
            p[0] = [ Product(p[2]) ]
            if isinstance(p[1],(list,tuple)) and len(p[1]) > 0:
                p[0] = p[0] + p[1]
        elif  len(p) == 2:
            p[0] = [ Product(p[1]) ]

    def p_prod_definition(self, p):
        """
         product : PRODUCT     product_prefix_list product_id attribute_list
                 | SMARTPHONE  product_prefix_list product_id attribute_list
        """
        p[0] = [ ProductAttribute('product', p[1]) ] 
        if isinstance(p[2],(list,tuple)) and len(p[2]) > 0:
            p[0] = p[0] + p[2]
        if isinstance(p[3],(list,tuple)) and len(p[3]) > 0:
            p[0] = p[0] + p[3]
        if isinstance(p[4],(list,tuple)) and len(p[4]) > 0:
            p[0] = p[0] + p[4]

    def p_prod_definition_no_header(self, p):
        """
         product :  product_id attribute_list
        """
        p[0] = p[1] 
        if isinstance(p[2],(list,tuple)) and len(p[2]) > 0:
            p[0] = p[0] + p[2]
                    
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
        p[0] = ProductAttribute('unlocked', 1)

        
    def p_product_prefix_numchip(self, p):
        """
        product_prefix : NUMCHIP           
        """
        p[0] = ProductAttribute('numchip', p[1])

    def p_product_prefix_provider(self, p):
        """
        product_prefix : PROVIDER          
        """
        p[0] = ProductAttribute('provider', p[1])

    def p_product_id(self, p):
        """
        product_id : BRAND ATTRIB attribute_list
                   
        """
        p[0] = [
            ProductAttribute('brand', p[1]),
            ProductAttribute('product_line', p[2]),
        ] 
        if isinstance(p[3],(list,tuple)) and len(p[3]) > 0:
            p[0] += p[3]
            
    def p_product_id_common_product_lines(self, p):
        """
        product_id :   BRAND common_product_lines attribute_list
                   |   common_product_lines attribute_list
        """
        if len(p) == 3:
            p[0] = p[1]
            if isinstance(p[2],(list,tuple)) and len(p[2]) > 0:
                p[0] += p[2]
        elif len(p) == 4:
            p[0] = p[2]
            if isinstance(p[3],(list,tuple)) and len(p[3]) > 0:
                p[0] += p[3]

    def p_common_product_lines_samsung(self, p):
        """
        common_product_lines : COMMON_PRODUCT_LINE_SAMSUNG
        """
        p[0] =  [ ProductAttribute('brand', 'samsung'), ProductAttribute('product_line', p[1]) ]

    def p_common_product_lines_sony(self, p):
        """
        common_product_lines : COMMON_PRODUCT_LINE_SONY
        """
        p[0] =  [ ProductAttribute('brand', 'sony'), ProductAttribute('product_line', p[1]) ]

    def p_common_product_lines_motorola(self, p):
        """
        common_product_lines : COMMON_PRODUCT_LINE_MOTOROLA
        """
        p[0] =  [ ProductAttribute('brand', 'motorola'), ProductAttribute('product_line', p[1]) ]

    def p_attribute_list(self, p):
        """
        attribute_list : attribute_list attribute
                       | attribute_list SEP attribute
                       | attribute
        """
        if len(p) == 2:
            if len([ p[1] ]) > 0:
                p[0] = [ p[1] ]
        elif len(p) == 3:
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
        p[0] = ProductAttribute('generic', p[1])

        
    def p_attribute_number_rep(self, p):
        """
        attribute : NUMBER
                  | FLOAT
        """
        p[0] = ProductAttribute('generic_num', p[1])


    def p_attribute_screen_diagonal(self, p):
        """
        attribute    : NUMBER INCHES
                     | FLOAT  INCHES
        """
        p[0] = ProductAttribute('screen_diagonal', p[1])
        
    def p_attribute_operating_system(self, p):
        """
        attribute  : OS_NAME NUMBER
                   | OS_NAME FLOAT
        """
        p[0] = ProductAttribute('operating_system', p[1])

    def p_attribute_storage(self, p):
        """
        attribute  :  NUMBER GIGABYTES
        """
        p[0] = ProductAttribute('storage', p[1])

    def p_attribute_provider(self, p):
        """
        attribute : PROVIDER          
        """
        p[0] = ProductAttribute('provider', p[1])

    def p_attribute_generation(self, p):
        """
        attribute : NUMBER ORDINAL GENERATION  
                  | LPAREN  NUMBER ORDINAL GENERATION RPAREN
        """
        if len(p) == 6:
            p[0] = ProductAttribute('generation', p[2])
        else:
            p[0] = ProductAttribute('generation', p[1])
        
    def p_attribute_tech(self, p):
        """
        attribute : TECHNOLOGY
        """
        p[0] = ProductAttribute('technology', p[1])

    def p_attribute_numchip(self, p):
        """
        attribute : NUMCHIP
        """
        p[0] = ProductAttribute('numchip', p[1])

    def p_attribute_color(self, p):
        """
        attribute : COLOR
        """
        p[0] = ProductAttribute('color', p[1])

    def p_attribute_lock(self, p):
        """
        attribute : UNLOCKED
        """
        p[0] = ProductAttribute('unlocked', 1)

    def p_attribute_mp3_player(self, p):
        """
        attribute : MP NUMBER
        """
        p[0] = ProductAttribute('mp3_player', 1)

    def p_attribute_camera(self, p):
        """
        attribute : camera_resolution
        """
        p[0] = p[1]

    def p_attribute_camera_resolution(self, p):
        """
        camera_resolution : NUMBER MP
                          | FLOAT  MP
        """
        p[0] = ProductAttribute('camera_resolution', p[1])
        
    def p_attribute_common_product_lines(self, p):
        """
        attribute : COMMON_PRODUCT_LINE_SAMSUNG
                  | COMMON_PRODUCT_LINE_SONY
                  | COMMON_PRODUCT_LINE_MOTOROLA
        """
        p[0] = ProductAttribute('product_line', p[1])
    
    def p_attribute_brand(self, p):
        """
        attribute : BRAND
        """
        p[0] = ProductAttribute('brand', p[1])

    def p_attribute_product(self, p):
        """
        attribute : PRODUCT
        """
        p[0] = ProductAttribute('product', p[1])
        
    def p_attribute_smartphone(self, p):
        """
        attribute : SMARTPHONE
                  | LPAREN SMARTPHONE RPAREN 
        """
        p[0] = ProductAttribute('product', 'smartphone')

    def p_error(self, p):
        if p:
           # print "Syntax error at '%s'" % p.value
            raise ParserException ( type    = 'Parser Exception',
                                    message ="Syntax error at '%s'" % p.value)
        else:
            #print "Syntax error at EOF"
            raise ParserException ( type    = 'Parser Exception',
                                    message ="Syntax error at EOF")
            
    def processList(self, list):
        if list is None:
            return
        for prod in list:
            if isinstance(prod,Product):
                print prod
            else:
                print "prrr!"
        
if __name__ == '__main__':

    file = './planilhas/sample-utf8.txt'
    if len(sys.argv) > 1:
        file = sys.argv[1]
    prod = MatchingParser(debug = 0, filename = file)
    prod.run()
    print "================"
    print "Num Prod Lines: %d"% prod.countProductLine;
    print "Num Models:     %d"% prod.countModel;
    
