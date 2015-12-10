import sys,re
import ply.lex as lex
import ply.yacc as yacc

from myParser import Product,ProductAttribute,Parser,ParserException
                                
class MatchingParser(Parser):
    tokens = (
        'PRODUCT',
        'ATTRIB','NUMBER','FLOAT','SEP', 
        ) 

    # Tokens
    t_SEP          = r'[\-\,\/\|\:\.\+\"]' 
    t_ATTRIB       = r'[a-zA-Z_][a-zA-Z0-9_]*'

    def t_PRODUCT(self,t):
        r'smartphone|capa|celular|telefone|case|pelicula|bateria|carregador|fone|ramal|adesivo|cabo|smartwatch|gondola'
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

    def p_prod_definition(self, p):
        """
         product : PRODUCT  attribute_list
        """
        p[0] = [ ProductAttribute('product', p[1]) ] 
        if isinstance(p[2],(list,tuple)) and len(p[2]) > 0:
            p[0] = p[0] +  p[2]
        p[0] = [ Product(p[0]) ]

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

    def p_attribute_product(self, p):
        """
        attribute : PRODUCT
        """
        p[0] = ProductAttribute('product', p[1])

    def p_error(self, p):
        if p:
           # print "Syntax error at '%s'" % p.value
            raise ParserException ( type    = 'Parser Exception',
                                    message ="Syntax error at '%s'" % (p.value) )
        else:
            #print "Syntax error at EOF"
            raise ParserException ( type    = 'Parser Exception',
                                    message ="Syntax error at EOF")
                                    
    def unitTest(self,line):
        prodList = yacc.parse(line)
        self.processList(prodList,line)
        self.prepareForMatching(prodList,line)
        assert prodList[0].getProductType() == 'smartphone'
        ## assert prodList[0].getProductBrand() == 'samsung'
        ## assert prodList[0].getProductRefcode() == 'A999'
        ## assert prodList[0].getModel() == 'galaxy s6'
        
if __name__ == '__main__':

    testfile = './planilhas/sample-utf8.txt'
    if len(sys.argv) > 1:
        file1 = sys.argv[1]

    test =  MatchingParser(debug = 0, filename = testfile, tag = 'Test')
    test.unitTest("smartphone samsung galaxy s6 A999 dual chip");
    test.dump()
    
    market = MatchingParser(debug = 0, filename = file1, tag = 'ARTIFACT')
    market.run()
    market.dumpProdList()

    

    
