'''
@author: amigur
'''

import string
import win32clipboard as w 
import win32con
from sys import exit
from Tkinter import *

############################################################################################
# Class SqlExprItem
class ElementType(object):
    (String, Other) = range(2)

class ParseError(Exception):
    def __init__(self, msg):
        self._msg = msg
    def __str__(self):
        return self._msg

############################################################################################
# Class LexElem
class LexElem(object):
    (StrConst, Identifier, Number, LPar, RPar, OperAssign, OperPlus, OperPlusAssign, Semicolon, Dot, Comma, End, Error) = range(13)
    
    @staticmethod
    def getLexElemName(lexElem):
        if lexElem == LexElem.StrConst:
            return "StrConst"
        if lexElem == LexElem.Identifier:
            return "Identifier"
        if lexElem == LexElem.Number:
            return "Number"
        if lexElem == LexElem.LPar:
            return "LPar"
        if lexElem == LexElem.RPar:
            return "RPar"
        if lexElem == LexElem.OperAssign:
            return "OperAssign"
        if lexElem == LexElem.OperPlus:
            return "OperPlus"
        if lexElem == LexElem.OperPlusAssign:
            return "OperPlusAssign"
        if lexElem == LexElem.Semicolon:
            return "Semicolon"
        if lexElem == LexElem.Dot:
            return "Dot"
        if lexElem == LexElem.Comma:
            return "Comma"
        if lexElem == LexElem.End:
            return "End"
        if lexElem == LexElem.Error:
            return "Error"
        return None

    @staticmethod
    def hasLexElemValue(lexElem):
        if lexElem in (LexElem.StrConst, LexElem.Identifier, LexElem.Number):
            return True
        return False


############################################################################################
# Class SimpleLexer
class SimpleLexer(object):
    
    def __init__(self, inputText):
        self._inputText = list(inputText)
        self.reset()
    
    def reset(self):
        self._index = 0 
        self._lexValue = None  
        self._lexElem = None
        self._stepBack = False
        self._lineNo = 1
    
    def _endStream(self):
        return self._index >= len(self._inputText)
    
    def _getChar(self):
        return self._inputText[self._index]

    def _nextChar(self):
        if not self._endStream():
            c = self._inputText[self._index]
            self._index +=  1
            return c
        return None
    
    def _readString(self):
        beginIndex = self._index
        ignore = False
        while not self._endStream():
            c = self._nextChar()
            if not ignore and c == '"':
                self._lexValue = self.getSubstr(beginIndex, self._index-1) 
                self._lexElem = LexElem.StrConst
                return self._lexElem
            ignore = (c == '\\')
        self._lexElem = LexElem.Error
        raise ParseError("unbalanced string constant.")
        
    def _readIdentifier(self):
        beginIndex = self._index - 1
        while not self._endStream():
            c = self._nextChar()
            if c != '_' and not c in string.ascii_letters and not c in string.digits:
                self._index -= 1
                break
        self._lexValue = self.getSubstr(beginIndex, self._index) 
        self._lexElem = LexElem.Identifier
        return self._lexElem 
            
    def _readNumber(self):
        beginIndex = self._index - 1
        while not self._endStream():
            c = self._nextChar()
            if c != '.' and not c in string.digits:
                self._index -= 1
                break
        self._lexValue = self.getSubstr(beginIndex, self._index) 
        self._lexElem = LexElem.Number
        return self._lexElem 

    def _eatLineComment(self):
        while not self._endStream() and not self._getChar() in ('\r','\n'):
            self._nextChar()
        if not self._endStream() and self._nextChar() == '\r' and not self._endStream() and self._getChar() == '\n':
            self._nextChar()
        self._lineNo += 1
    
    def _eatMultiLineComment(self):
        while not self._endStream():
            c = self._nextChar()
            if c == '*' and not self._endStream() and self._getChar() == '/':
                self._nextChar()
                break
    
    def getIndex(self):
        return self._index 
    
    def getSubstr(self, beginIndex, endIndex):
        return string.join(self._inputText[beginIndex: endIndex],"") 

    def eatWhiteSpace(self):
        if not self._endStream():
            beginIndex = self._index
            while not self._endStream() and self._getChar() in string.whitespace:
                if self._getChar() == '\n':
                    self._lineNo += 1
                self._nextChar()
            return self.getSubstr(beginIndex, self._index) 
        return ""

    def getElem(self):
        return self._lexElem

    def nextElem(self):
        
        if self._stepBack:
            self._stepBack = False
            return self._lexElem
        
        if self._lexElem == LexElem.Error:
            return self._lexElem
        
        self._lexValue = None

        self.eatWhiteSpace()
        
        if self._index >= len(self._inputText):
            self._lexElem = LexElem.End
            return self._lexElem
        
        c = self._nextChar()
        
        # Read comment
        if c == '/':
            if not self._endStream(): 
                if self._getChar() == '/':
                    self._nextChar()
                    self._eatLineComment()
                    return self.nextElem() 
                if self._getChar() == '*':
                    self._nextChar()
                    self._eatMultiLineComment()
                    return self.nextElem()
        
        self._lexValue = c                
        
        if c in ( '(', '[' ):
            self._lexElem = LexElem.LPar
            return self._lexElem

        if c in ( ')', ']'):
            self._lexElem = LexElem.RPar
            return self._lexElem

        if c == '=':
            self._lexElem = LexElem.OperAssign   
            return self._lexElem

        if c == ';':
            self._lexElem = LexElem.Semicolon   
            return self._lexElem

        if c == ',':
            self._lexElem = LexElem.Comma   
            return self._lexElem

        if c == '.':
            self._lexElem = LexElem.Dot   
            return self._lexElem

        if c == ',':
            self._lexElem = LexElem.Comma   
            return self._lexElem

        if c == '+':
            if not self._endStream() and self._getChar() == '=':
                self._lexValue += "="
                self._nextChar()
                self._lexElem = LexElem.OperAssign
            else:
                self._lexElem = LexElem.OperPlus
            return self._lexElem

        if c == '"':
            return self._readString()
        
        if c in string.ascii_letters or c == '_':
            return self._readIdentifier()

        if c in string.digits:
            return self._readNumber()
       
        self._lexElem = LexElem.Error
        raise ParseError("uknown symbol : " + c)
        
    def getLexValue(self):
        return self._lexValue
    
    def getLineNo(self):
        return self._lineNo
    
    def stepBack(self):
        self._stepBack = True 


############################################################################################
# Class SqlParser
class SqlParser(object):
    
    def __init__(self, text):
        self._lexer = SimpleLexer(text)
        self._variable = None
        self._elemList = ()
        self._isStrBufferExpr = None
        self._parseError = False
        self._errMsg = None
        self._startExpression = ""
        self._startSpacing = "\t"
  
    def _checkSemicolon(self):
        if self._lexer.nextElem() != LexElem.Semicolon:
            raise ParseError("semicolon missing.")

    def _readVarIdentif(self, start=False):
        if self._lexer.nextElem() != LexElem.Identifier:
            if self._variable == None:
                raise ParseError("identifier expected.")    
            elif self._lexer.getElem() != LexElem.End:
                raise ParseError("'" + self._variable + "' expected.")    
            return (None, None) 

        variable = self._lexer.getLexValue()

        while self._lexer.nextElem() == LexElem.Dot:
            if self._lexer.nextElem() == LexElem.Identifier:
                variable += "." + self._lexer.getLexValue()
                if self._lexer.getLexValue() == "append":
                    return (True, variable)
            else:
                if self._variable == None:    
                    raise ParseError("identifier expected.")    
                else:
                    raise ParseError("'" + self._variable + "' expected.")    
        self._lexer.stepBack()
        if start:
            if variable == "String":
                result = self._readVarIdentif(start=False)
                self._startExpression = self._startSpacing + "String " + result[1]
                return result
            self._startExpression = self._startSpacing + variable
        return (False, variable)


    def _parseInnerSubExpr(self, beginIndex, parCount):
        while self._lexer.getElem() != LexElem.End:
            endIndex = self._lexer.getIndex()
            elem = self._lexer.nextElem()
            if parCount == 0: 
                if self._isStrBufferExpr and elem in (LexElem.OperPlus, LexElem.RPar) or \
                   not self._isStrBufferExpr and elem in (LexElem.OperPlus, LexElem.Semicolon):
                    self._elemList += ((ElementType.Other, self._lexer.getSubstr(beginIndex, endIndex)),)
                    self._lexer.stepBack()
                    return
            if elem==LexElem.LPar:
                parCount += 1
            elif elem==LexElem.RPar:
                parCount -= 1
        
        raise ParseError("Unexpected end of expression.")    
   
    def _parseInnerExpr(self):
        while True:
            beginIndex = self._lexer.getIndex()
            elem = self._lexer.nextElem()
            if self._isStrBufferExpr and elem == LexElem.RPar:
                self._lexer.stepBack()
                break
            if not self._isStrBufferExpr and elem == LexElem.Semicolon:
                self._lexer.stepBack()
                break
            elif elem == LexElem.StrConst:
                self._elemList += ((ElementType.String, self._lexer.getLexValue()),)
            elif elem == LexElem.OperPlus:
                pass
            elif elem == LexElem.LPar:
                self._parseInnerSubExpr(beginIndex, 1)
            elif elem in (LexElem.Identifier, LexElem.Number):
                self._parseInnerSubExpr(beginIndex, 0)
            else:
                raise ParseError("unexpected token <" + LexElem.getLexElemName(self._lexer.getElem()) + ">")    

    def _parseStrBufferRExpr(self):
        if self._lexer.nextElem() != LexElem.LPar:
            raise ParseError("left parenthesis expected.")    
        
        self._parseInnerExpr()

        if self._lexer.nextElem() != LexElem.RPar:
            raise ParseError("right parenthesis expected.")    

        self._checkSemicolon()
    
    def _parseStrBufferExprBlock(self):
        '''
        parses block of string buffer expressions
        '''
        while self._lexer.getElem() != LexElem.End:
            (_, variable) = self._readVarIdentif()
            if self._lexer.getElem() != LexElem.End:
                if variable != self._variable:
                    raise ParseError("'" + self._variable + "' expected.")    
                else:
                    self._parseStrBufferRExpr()

    def _parseStringRExpr(self, start=False):
        operElem = self._lexer.nextElem()
        if not operElem in (LexElem.OperAssign, LexElem.OperPlusAssign):
            raise ParseError("operators '=' or '+=' expected.")
        if start:
            self._startExpression += " " + self._lexer.getLexValue()       
        self._parseInnerExpr()
        self._checkSemicolon()

    def _parseStringExprBlock(self):
        '''
        parses block of string expressions
        '''
        while self._lexer.getElem() != LexElem.End:
            (_, variable) = self._readVarIdentif()
            if self._lexer.getElem() != LexElem.End:
                if variable != self._variable:
                    raise ParseError("'" + self._variable + "' expected.")    
                else:
                    self._parseStringRExpr()

    def hasError(self):
        return self._parseError
        
    def getErrorMsg(self):
        return self._parseError and self._errMsg or ""
    
    def getStartExpression(self):
        return self._startExpression
    
    def getElemList(self):
        return self._elemList
    
    def getStartSpacing(self):
        return self._startSpacing  
            
    def printElemList(self):
        '''
        Print parsed element list 
        '''
        for t in self._elemList:
            if t[0] == ElementType.String:
                print "String : ",
            elif t[0] == ElementType.Other:  
                print "Expr   : ",
            print t[1]

    def extractString(self):
        '''
        Extracts and concates String expressions from input  text
        '''
        extractedValue = ""
        while self._lexer.getElem() != LexElem.End:
            lexElem = self._lexer.nextElem()
            if lexElem == LexElem.StrConst:
                extractedValue += self._lexer.getLexValue()
            if lexElem == LexElem.End:
                break 
        return extractedValue

    def parse(self):
        '''
        Parses input text, returns True if parsing is succesfull 
        '''
        self._lexer.reset()
        self._parseError = False
        
        try:
            spacing = self._lexer.eatWhiteSpace().rsplit("\n",1)
            self._startSpacing = spacing[len(spacing)-1]
            (self._isStrBufferExpr, self._variable) = self._readVarIdentif(start=True)
            
            if self._isStrBufferExpr:
                self._parseStrBufferRExpr()
                self._parseStrBufferExprBlock()
            else:
                self._parseStringRExpr(start=True)
                self._parseStringExprBlock()
        except ParseError as e:
            self._parseError = True
            self._errMsg = "Line " + str(self._lexer.getLineNo()) + " : " + str(e)
            
        return not self._parseError
                    
############################################################################################
# Class SqlFormatter
class SqlFormatter(object):
    
    beginClauses = {"left", "right", "inner", "outer", "group", "order", "union"}
    endClauses = {"where", "set", "having", "join", "from", "by", "join", "into", "intersect", "minus", "select", "on"}
    logical = {"and", "or", "when", "else", "end"}
    quantifiers = {"in", "all", "exists", "some", "any"}
    dml = {"insert", "update", "delete"}
    
    toksep = "()+*/-=<>'`\"[]," + string.whitespace
    
    def __init__(self):
        self.reset()

    def reset(self):
        self._startIndent = ""
        self._indentString = "\t\t"
        self._beginLine = True
        self._afterBeginBeforeEnd = False
        self._afterByOrSetOrFromOrSelect = False
        self._afterOn = False
        self._afterBetween = False
        self._afterInsert = False
        self._inFunction = 0
        self._parensSinceSelect = 0
        self._parenCounts = []
        self._afterByOrFromOrSelects = []
        self._indent = 1
        self._lastToken = None
        self._token = None 
        self._lcToken = None
        self._result = ""
        self._stringStarted = False
        self._wasOther = False 
        self._sqlIdentifiers = SqlFormatter.logical.union(SqlFormatter.endClauses).union(SqlFormatter.quantifiers).union(SqlFormatter.dml)

    def _out(self, upper=False):
        if not self._stringStarted:
            self._result += "\""
            self._stringStarted = True
        if upper:
            self._result += self._token.upper()
        else:
            self._result += self._token
    
    def _newline(self):
        if self._stringStarted:
            if not self._result.endswith(" "):
                self._result += " "
            self._result += "\" +"
            self._stringStarted = False
            
        self._result += "\n"
        
        self._result += self._startIndent
        
        for _ in range(self._indent):
            self._result += self._indentString
            
        self._beginLine = True

    def _commaAfterByOrFromOrSelect(self):
        self._out()
        self._newline()
    
    def _commaAfterOn(self):
        self._out()
        self._indent -= 1
        self._newline()
        self._afterOn = False
        self._afterByOrSetOrFromOrSelect = True
    

    def _isFunctionName(self, name):
        isIdentif = name[0] in string.ascii_letters + '_'+ '"' 
        return isIdentif and not name in self._sqlIdentifiers  
    
    def _openParen(self):
        if self._isFunctionName( self._lastToken ) or self._inFunction > 0: 
            self._inFunction += 1

        self._beginLine = False
        
        if self._inFunction > 0:
            self._out()
        else:
            self._out()
            if not self._afterByOrSetOrFromOrSelect:
                self._indent += 1
                self._newline()
                self._beginLine = True
            else:
                self._indent += 1
        self._parensSinceSelect += 1
    
    def _closeParen(self):
        self._parensSinceSelect -= 1

        if self._parensSinceSelect < 0:
            self._indent -= 1
            self._parensSinceSelect = self._parenCounts.pop()
            self._afterByOrSetOrFromOrSelect = self._afterByOrFromOrSelects.pop()

        if self._inFunction > 0:
            self._inFunction -= 1
            self._out()
        else:
            if not self._afterByOrSetOrFromOrSelect:
                self._indent -= 1
                self._newline()
            self._out()

        self._beginLine = False
    
    
    def _beginNewClause(self):
        if not self._afterBeginBeforeEnd:
            if self._afterOn:
                self._indent -= 1
                self._afterOn = False
            self._indent -= 1
            self._newline()
        self._out(upper=True)
        self._beginLine = False
        self._afterBeginBeforeEnd = True
    
    def _endNewClause(self):
        if not self._afterBeginBeforeEnd:
            self._indent -= 1
            if self._afterOn:
                self._indent -= 1
                self._afterOn = False
            self._newline()
        
        self._out(upper=True)
        
#        if self._lcToken != "union":
        self._indent += 1
        self._newline()
        self._afterBeginBeforeEnd = False
        self._afterByOrSetOrFromOrSelect = self._lcToken in ("by", "set", "from")
    
    
    def _select(self):
        self._out(upper=True)
        self._indent += 1
        self._newline()
        self._parenCounts.append(self._parensSinceSelect)
        self._afterByOrFromOrSelects.append(self._afterByOrSetOrFromOrSelect)
        self._parensSinceSelect = 0
        self._afterByOrSetOrFromOrSelect = True
    
    def _updateOrInsertOrDelete(self):
        self._newline()
        self._out(upper=True)
        self._indent += 1
        self._beginLine = False
        if self._lcToken == "update":
            self._newline()
        if self._lcToken == "insert":
            self._afterInsert = True
    
    def _values(self):
        self._indent -= 1
        self._newline()
        self._out()
        self._indent += 1
        self._newline()
    
    def _on(self):
        self._indent += 1
        self._afterOn = True
        self._newline()
        self._out()
        self._beginLine = False
    
    def _logical(self):
        if self._lcToken == "end":
            self._indent -= 1
        self._newline()
        self._out(upper=True)
        self._beginLine = False
    
    
    def _white(self):
        if not self._beginLine:
            if not self._stringStarted:
                self._result += "\""
                self._stringStarted = True
            self._result += " "
    
    def _misc(self):
        self._out()
        if self._lcToken == "between":
            self._afterBetween = True
        if self._afterInsert:
            self._newline()
            self._afterInsert = False
        else:
            self._beginLine = False
            if self._lcToken == "case":
                self._indent += 1

    def _processString(self, it, endSymbol):
        self._wasOther = False
        while True:
            tokt = it.next()
            
            if self._wasOther:
                self._result += " + "
                self._wasOther = False
                self._beginLine = False
            
            if tokt[0] == ElementType.String:
                self._token += tokt[1]
                if tokt[1] == endSymbol:
                    self._wasOther = False
                    break
            else:
                self._out()
                self._token = ""
                self._processOtherToken(it, tokt)
    
    def _processStringToken(self, it, tokt):
        self._token = tokt[1]
        self._lcToken = self._token.lower()
        
        if self._token == "'":
            self._processString(it, "'")
        elif self._token == "\"" :
            self._processString(it, '"')

        if self._afterByOrSetOrFromOrSelect and self._token == ",":
            self._commaAfterByOrFromOrSelect()
        elif self._afterOn and self._token == ",":
            self._commaAfterOn()
        elif self._token == "(":
            self._openParen()
        elif self._token == ")":
            self._closeParen()
        elif self._lcToken in SqlFormatter.beginClauses:
            self._beginNewClause()
        elif self._lcToken in SqlFormatter.endClauses:
            self._endNewClause()
        elif self._lcToken == "select":
            self._select()
        elif self._lcToken in SqlFormatter.dml:
            self._updateOrInsertOrDelete()
        elif self._lcToken == "values":
            self._values()
        elif self._lcToken == "on":
            self._on()
        elif self._afterBetween and self._lcToken == "and":
            self._misc()
            self._afterBetween = False
        elif self._lcToken in SqlFormatter.logical:
            self._logical()
        elif string.whitespace.find(self._token) >= 0:
            self._white()
        else:
            self._misc()

        if string.whitespace.find(self._token) == -1:
            self._lastToken = self._lcToken
    
    def _processOtherToken(self, it, tokt):
        if self._stringStarted:
            self._result += "\" + "
            self._stringStarted = False
        self._result += tokt[1]
        self._wasOther = True

    def _tokenize(self, val):
        result = ()
        tok = ""
        for c in val:
            if c in SqlFormatter.toksep:
                if len(tok) > 0:
                    result += (tok,)
                    tok = ""
                result += (str(c),)
            else:
                tok += c
        if len(tok) > 0:
            result += (tok,)
        return result
    
    def _prepareTokenList(self, elList):
        result = ()
        for (elType, val) in elList:
            if elType == ElementType.Other:
                result += ((elType, val),)
            else:
                for tok in self._tokenize(val):
                    result += ((ElementType.String, tok),)
        return result
    
    def setStartIndent(self, startIndent):
        self._startIndent = startIndent

    def formatSql(self, elList):
        self._result = ""
        
        it = iter(self._prepareTokenList(elList))
        self._wasOther = False
        try:
            while True:
                tokt = it.next()
                if self._wasOther:
                    self._result += " + "
                    self._wasOther = False
                    self._beginLine = False
                if tokt[0] == ElementType.String:
                    self._processStringToken(it, tokt)
                else:
                    self._processOtherToken(it, tokt)
        except StopIteration:
            if self._stringStarted:
                self._result += "\""
        
        return self._result 

def getText(): 
    w.OpenClipboard() 
    d=w.GetClipboardData(win32con.CF_TEXT) 
    w.CloseClipboard() 
    return d 
 
def setText(aString): 
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(win32con.CF_TEXT,aString) 
    w.CloseClipboard()

text=getText()
parser = SqlParser(text)

if parser.parse():
    formatter = SqlFormatter()
    formatter.setStartIndent(parser.getStartSpacing() + "\t")
    fmtString = parser.getStartExpression() + formatter.formatSql(parser.getElemList()) + ";"
    setText(fmtString)
else:
    root = Tk() 
    Label(root, text=parser.getErrorMsg()).pack() 
    Button(root, text='ERROR', command=exit).pack() 
    root.mainloop()

