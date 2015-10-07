import sys,re
import ply.lex as lex
import ply.yacc as yacc

from myParser import Product,ProductAttribute,Parser,ParserException
                                
class MatchingParser(Parser):
    tokens = (
        'BRAND','PRODUCT','TECHNOLOGY', 'COLOR','NUMCHIP',
        'ATTRIB','NUMBER','FLOAT','SEP', 'UNLOCKED','GIGABYTES',
        'MP','INCHES','PROVIDER','OS_NAME','GPS','VENDOR',
        'COMMON_PRODUCT_LINE_SAMSUNG','SMARTPHONE','WATERPROOF',
        'COMMON_PRODUCT_LINE_SONY','GENERATION', 'ORDINAL',
        'COMMON_PRODUCT_LINE_MOTOROLA','LPAREN','RPAREN',
        'PROCESSOR_TYPE',
        'PROCESSOR',
        # 'GHZ',
        ) 

    # Tokens
    t_LPAREN	   = r'\('
    t_RPAREN	   = r'\)'
    t_SEP          = r'[\-\,\/\|\:\.\+]' 
    t_INCHES       = r'[\"]|\'[\s]?\'' 
    t_ATTRIB       = r'[a-zA-Z_][a-zA-Z0-9_]*'

    def t_GPS(self,t):
        r'a\-gps|gps'
        return t
    
    # def t_GHZ(self,t):
    #     r'ghz'
    #     return t
    
    def t_PROCESSOR_TYPE(self,t):
        r'(single|dual|quad|octa)[ \-]core'
        return t
    
    def t_PROCESSOR(self,t):
        r'processador'
        return t
    
    def t_WATERPROOF(self,t):
        r'resistente.*agua|a.*agua'
        return t
    
    def t_VENDOR(self,t):
        r'frete.*webfones|webfones'
        return t

    def t_COLOR(self,t):
        r'azul|branco|preto|prata|dourado|titanio|verde|grafite|vermelho|rosa|roxo'
        return t

    def t_UNLOCKED(self,t):
        r'desbloqueado'
        return t

    def t_ORDINAL(self,t):
        r'a\b'
        return t

    def t_TECHNOLOGY(self,t):
        r'3g|4g|gsm'
        return t

    def t_GIGABYTES(self,t):
        r'gb\b'
        return t

    def t_MP(self,t):
        r'mp'
        return t

    def t_PROVIDER(self,t):
        r'\bclaro\b|\boi\b|\btim\b|\bvivo\b'
        return t

    def t_GENERATION(self,t):
        r'geracao[.]?'
        return t
    
    def t_NUMCHIP(self,t):
        r'(dual|tri|quad)\s+(sim|chip)'
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
        t.lexer.skip(1)
        raise ParserException (type    = 'Lexical Exception',
                               message ="Illegal character '%s'" % t.value[0])

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

    # def p_attribute_processor(self, p):
    #     """
    #     attribute  : PROCESSOR_TYPE
    #                | PROCESSOR PROCESSOR_TYPE
    #     """
    #     if   len(p) == 2:
    #         p[0] = ProductAttribute('processor_numcore', p[1]) 
    #     elif len(p) == 3:
    #         p[0] = ProductAttribute('processor_numcore', p[2]) 

    def p_attribute_processor_ignore(self, p):
        """
        attribute  : PROCESSOR
        """
        pass
        
    def p_attribute_processor_type(self, p):
        """
        attribute  : PROCESSOR_TYPE
        """
        p[0] = ProductAttribute('processor_numcore', p[1]) 

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

    def p_attribute_waterproof(self, p):
        """
        attribute : WATERPROOF
        """
        p[0] = ProductAttribute('waterproof', 1)

    def p_attribute_gps(self, p):
        """
        attribute : GPS
        """
        p[0] = ProductAttribute('gps', 1)


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

    def p_attribute_vendor(self, p):
        """
        attribute : VENDOR
        """
        pass
    
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

        
if __name__ == '__main__':

    file = './planilhas/sample-utf8.txt'
    if len(sys.argv) > 1:
        file1 = sys.argv[1]
    if len(sys.argv) > 2:
        file2 = sys.argv[2]
    market = MatchingParser(debug = 0, filename = file1)
    market.run()
    print ">>>>>>>>>>>>>>>>>>"
    market.dump()
    offers = MatchingParser(debug = 0, filename = file2)
    offers.run()
    print "<<<<<<<<<<<<<<<<<<"
    offers.dump()
    offers.match(market)
    print "================"
    print "1) Num Prod Lines: %d"% market.countProductLine;
    print "   Num Models:     %d"% market.countModel;
    print "2) Num Prod Lines: %d"% offers.countProductLine;
    print "   Num Models:     %d"% offers.countModel;
    
