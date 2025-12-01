TT_INT    = 'INT'
TT_FLOAT  = 'FLOAT'
TT_SUM    = 'SUM'
TT_MINUS  = 'MINUS'
TT_MULT   = 'MULT'
TT_DIV    = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF    = 'EOF'
TT_EQ     = 'EQ'
TT_ID     = 'ID'


class Erro(Exception):
    def __init__(self, posInicio, posFinal, nomeDoErro, detalheDoErro):
        super().__init__(f'{nomeDoErro}: {detalheDoErro}')
        self.posInicio = posInicio
        self.posFinal = posFinal
        self.nomeDoErro = nomeDoErro
        self.detalhedoErro = detalheDoErro
    
    def printDoErro(self):
        resultado  = f'{self.nomeDoErro}: {self.detalhedoErro}\n'
        resultado += f'Posicao do Erro -> Linha: {self.posInicio.linha}, Coluna: {self.posInicio.coluna}\n'
        resultado += f'Arquivo: {self.posInicio.nomeArquivo}'
        return resultado
    

class ErroCaractereInvalido(Erro):
    def __init__(self, posInicio, posFinal, detalheDoErro):
        super().__init__(posInicio, posFinal, 'Erro de Caractere Inválido', detalheDoErro)


class ErroSintaxeInvalida(Erro):
    def __init__(self, detalheDoErro, posErro=None):
        if posErro is None:
            posErro = Posicao(0, 0, 0, 'Desconhecido')
        super().__init__(posErro, posErro, 'Erro de Sintaxe', detalheDoErro)


class ErroExecucao(Erro):
    def __init__(self, detalheDoErro, posErro=None):
        if posErro is None:
            posErro = Posicao(0, 0, 0, 'Execução')
        super().__init__(posErro, posErro, 'Erro de Execução', detalheDoErro)


class Posicao:
    def __init__(self, indice, linha, coluna, nomeArquivo):
        self.indice = indice
        self.linha = linha
        self.coluna = coluna
        self.nomeArquivo = nomeArquivo

    def avancar(self, atual = None):
        self.indice += 1
        self.coluna += 1        

        if atual == '\n':
            self.coluna = 0
            self.linha += 1
        
        return self
    
    def copia(self):
        return Posicao(self.indice, self.linha, self.coluna, self.nomeArquivo)


class Token:
    def __init__(self, tipo, valor = None):
        self.tipo = tipo
        self.valor = valor

    def __repr__(self):
        if self.valor is not None:
            return f'{self.tipo}: {self.valor}'
        return f'{self.tipo}'


class Lexer:
    def __init__(self, nomeArquivo, texto):
        self.texto = texto
        self.pos = Posicao(-1, 0, -1, nomeArquivo)
        self.atual = None
        self.avancar()

    def avancar(self):
        self.pos.avancar(self.atual)
        if self.pos.indice < len(self.texto):
            self.atual = self.texto[self.pos.indice]
        else:
            self.atual = None
    
    def makeToken(self):
        tokens = []

        while self.atual is not None:
            if self.atual.isspace():
                self.avancar()

            elif self.atual.isdigit():
                tokens.append(self.floatOrInt())    

            elif self.atual == '+':
                tokens.append(Token(TT_SUM))
                self.avancar()

            elif self.atual == '-':
                tokens.append(Token(TT_MINUS))
                self.avancar()

            elif self.atual == '/':
                tokens.append(Token(TT_DIV))
                self.avancar()   

            elif self.atual == '*':
                tokens.append(Token(TT_MULT))
                self.avancar()

            elif self.atual == '(':
                tokens.append(Token(TT_LPAREN))
                self.avancar()   

            elif self.atual == ')':
                tokens.append(Token(TT_RPAREN))
                self.avancar()   

            elif self.atual == '=':
                tokens.append(Token(TT_EQ))
                self.avancar()

            elif self.atual.isalpha() or self.atual == '_':
                tokens.append(self.makeID())

            else:
                posInicio = self.pos.copia()
                char = self.atual
                self.avancar()
                return [], ErroCaractereInvalido(posInicio, self.pos, char)

        tokens.append(Token(TT_EOF))
        return tokens, None
    
    def floatOrInt(self):
        contadorDePontos = 0
        numStr = ''

        while self.atual is not None and (self.atual.isdigit() or self.atual == '.'):
            if self.atual == '.':
                if contadorDePontos == 1:
                    break
                contadorDePontos += 1
                numStr += self.atual
            else:
                numStr += self.atual
            self.avancar()

        if contadorDePontos == 1:
            return Token(TT_FLOAT, float(numStr))
        else:
            return Token(TT_INT, int(numStr))
        
    def makeID(self):
        idString = ''

        while self.atual is not None and (self.atual.isalpha() or self.atual == '_'):
            idString += self.atual
            self.avancar()
        
        return Token(TT_ID, idString)


class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'


class OpBinario:
    def __init__(self, left, operadorToken, right):
        self.left = left
        self.operadorToken = operadorToken
        self.right = right

    def __repr__(self):
        return f'({self.left}, {self.operadorToken}, {self.right})'
    

class VarAcessNode:
    def __init__(self, token):
        self.token = token


class VarAssignNode:
    def __init__(self, token, valorNode):
        self.token = token
        self.valorNode = valorNode


class PrintNode:
    def __init__(self, valorNode):
        self.valorNode = valorNode

###
class InputNode:
    def __init__(self, token):
        self.token = token


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokenIndex = -1
        self.tokenAtual = None
        self.avancar()

    def avancar(self):
        self.tokenIndex += 1
        if self.tokenIndex < len(self.tokens):
            self.tokenAtual = self.tokens[self.tokenIndex]
        else:
            self.tokenAtual = Token(TT_EOF)
        return self.tokenAtual
    
    def voltar(self):
        self.tokenIndex -= 1
        self.tokenAtual = self.tokens[self.tokenIndex]
    
    def factor(self):
        tok = self.tokenAtual

        if tok.tipo in (TT_INT, TT_FLOAT):
            node = NumberNode(tok)
            self.avancar()
            return node
        
        if tok.tipo == TT_ID:
            self.avancar()
            return VarAcessNode(tok)
        
        if tok.tipo == TT_LPAREN:
            self.avancar()
            exprNode = self.expr()
            if self.tokenAtual.tipo == TT_RPAREN:
                self.avancar()
                return exprNode
            raise ErroSintaxeInvalida("Esperava encontrar ')'")

        raise ErroSintaxeInvalida("Esperava número, variável ou '('")


    def term(self):
        left = self.factor()
        
        while self.tokenAtual.tipo in (TT_MULT, TT_DIV):
            operador = self.tokenAtual
            self.avancar()
            right = self.factor()
            left = OpBinario(left, operador, right)
        
        return left
    
    def expr(self):
        left = self.term()
        
        while self.tokenAtual.tipo in (TT_SUM, TT_MINUS):
            operador = self.tokenAtual
            self.avancar()
            right = self.term()
            left = OpBinario(left, operador, right)
        
        return left
    
    def statment(self):
        tok = self.tokenAtual

        if tok.tipo == TT_ID and tok.valor == 'PRINT':
            self.avancar()
            expr = self.expr()
            return PrintNode(expr)
        
        ###
        if tok.tipo == TT_ID and tok.valor == 'INPUT':
            self.avancar()
            if self.tokenAtual.tipo != TT_ID:
                raise ErroSintaxeInvalida("Esperava uma variavel após INPUT")
            varToken = self.tokenAtual
            self.avancar()
            return InputNode(varToken)
        
        if tok.tipo == TT_ID:
            varAux = tok
            self.avancar()

            if self.tokenAtual.tipo == TT_EQ:
                self.avancar()
                valorNode = self.expr()
                return VarAssignNode(varAux, valorNode)
            else:
                self.voltar()

        return self.expr()
    
    def parse(self):
        resultado = self.statment()
        if self.tokenAtual.tipo != TT_EOF:
            raise ErroSintaxeInvalida("Símbolos extras após o fim da expressão")
        return resultado


nomeVariaveis = {}

def avaliador(Node):

    if isinstance(Node, NumberNode):
        return Node.token.valor
    
    if isinstance(Node, VarAcessNode):
        nome = Node.token.valor

        if nome not in nomeVariaveis:
            raise ErroExecucao(f"Variável '{nome}' não foi declarada antes.")
        
        return nomeVariaveis[nome]
    
    if isinstance(Node, VarAssignNode):
        nome = Node.token.valor
        valor = avaliador(Node.valorNode)
        nomeVariaveis[nome] = valor
        return valor
    
    if isinstance(Node, PrintNode):
        valor = avaliador(Node.valorNode)
        print(valor)
        return valor
    
    ###
    if isinstance(Node, InputNode):
        nome = Node.token.valor
        expressao = input(f"{nome}: ")

        partes = expressao.replace("+", " ").replace("-", " ").replace("*", " ").replace("/", " ").split()
        for aux in partes:
            if aux.isalpha() and aux not in nomeVariaveis:
                raise ErroSintaxeInvalida(f"Variável '{aux}' não declarada")
        
        resultado, erro = run("input", expressao)
        if erro:
            raise erro

        nomeVariaveis[nome] = resultado
        return resultado
        
    
    if isinstance(Node, OpBinario):
        left = avaliador(Node.left)
        right = avaliador(Node.right)

        tipo = Node.operadorToken.tipo

        if tipo == TT_SUM:
           return left + right
        if tipo == TT_MINUS:
            return left - right
        if tipo == TT_DIV:
            return left / right
        if tipo == TT_MULT:
            return left * right
        
        raise ErroExecucao('Símbolo de expressão desconhecido')
    
    raise ErroExecucao('Nó desconhecido no avaliador')

def run(nomeArquivo, texto):
    lexer = Lexer(nomeArquivo, texto)
    tokens, erro = lexer.makeToken()

    if erro is not None:
        return None, erro
    
    parser = Parser(tokens)
    arvOp = parser.parse()

    resultado = avaliador(arvOp)

    return resultado, None