import sys,re
import ply.lex as lex
import ply.yacc as yacc
import os
from parser import ProductAttribute, Parser, ParserException

                                
class MatchingParser(Parser):
    tokens = (
        'BRAND','PRODUCT','TECHNOLOGY', 'COLOR','NUMCHIP',
        'ATTRIB','NUMBER','FLOAT','SEP', 'UNLOCKED','GIGABYTES',
        'MEGAPIXELS', 'MP3','INCHES','PROVIDER','OS_NAME',
        'COMMON_PRODUCT_LINE_SAMSUNG','SMARTPHONE',
        'COMMON_PRODUCT_LINE_SONY',
        'COMMON_PRODUCT_LINE_MOTOROLA',
        ) 

    # Tokens
    
    t_SEP          = r'[\-\,\/\|\:\.\+]' 
    t_INCHES       = r'[\"]' 
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

    def t_GIGABYTES(self,t):
        r'gb\b'
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

    def t_COMMON_PRODUCT_LINE_SAMSUNG(self,t):
        r'galaxy'
        return t

    def t_COMMON_PRODUCT_LINE_SONY(self,t):
         r'xperia'
         return t
        
    def t_COMMON_PRODUCT_LINE_MOTOROLA(self,t):
         r'moto\b'
         return t

    def t_SMARTPHONE(self,t):
         r'smartphone\b'
         return t

    def t_PRODUCT(self,t):
        r'smart\s+tv|capa|viva[\-\s]voz|suporte|pen[ \-]drive|celular|controle|camera|fone|kit|fonte|monofone|carregador|bracadeira|joystick|cabo|bastao'
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
        #print "Illegal character '%s'" % t.value[0]
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
            p[0] = p[1] + p[2]
        elif  len(p) == 2:
            p[0] = p[1] 

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
        p[0] = ProductAttribute('screen_diagonal', p[1])
        
    def p_attribute_camera_resolution(self, p):
        """
        camera_resolution : NUMBER MEGAPIXELS
                          | FLOAT  MEGAPIXELS
        """
        p[0] = ProductAttribute('camera_resolution', p[1])

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
        attribute : MP3
        """
        p[0] = ProductAttribute('mp3_player', 1)

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

    def p_error(self, p):
        if p:
           # print "Syntax error at '%s'" % p.value
           raise ParserException ( type    = 'Parser Exception',
                                    message ="Syntax error at '%s'" % p.value)
        else:
            # print "Syntax error at EOF"
            raise ParserException ( type    = 'Parser Exception',
                                     message ="Syntax error at EOF")

    def processList(self, attribList):
        # get first 'product_line' feature
        if not isinstance(attribList,list):
            return
        product_line    = next((feature for feature in attribList if feature.get_type() == 'product_line'), None)
        if product_line is not None:
            # get first product_line's index
            self.countProductLine += 1
            product_line_ix = next(i for i, feature in enumerate(attribList) if feature.get_type() == 'product_line')
            max_model_value = ""
            count = product_line_ix
            model_value = None
            model_value_ix = -1
            contains_digits = re.compile('\d')
            for f in attribList[product_line_ix:]:
                if isinstance(f,ProductAttribute) and f.get_type() in ('generic','product_line','generic_num'):
                    value = f.get_value()
                    # does feature value contain digits ?
                    if bool(contains_digits.search(value)): 
                        if (len(value) > len(max_model_value)):
                            max_model_value = value
                            model_value = f
                            model_value_ix = count
                else:
                    break
                count += 1
            # print ">>> %s (%d), %s (%d)"  % (product_line,product_line_ix, model_value,model_value_ix)
            if model_value is not None and product_line != model_value: 
                model_value.set_type('model')
                self.countModel += 1
            for attrib in attribList:
                if isinstance(attrib,ProductAttribute):
                    print attrib                
        
if __name__ == '__main__':

    file = './planilhas/sample-utf8.txt'
    if len(sys.argv) > 1:
        file = sys.argv[1]
    prod = MatchingParser(debug = 0, filename = file)
    prod.run()
    print "================"
    print "Num Prod Lines: %d"% prod.countProductLine;
    print "Num Models:     %d"% prod.countModel;
    