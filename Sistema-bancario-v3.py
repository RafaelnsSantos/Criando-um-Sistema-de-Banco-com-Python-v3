from abc import ABC,abstractmethod
from datetime import datetime
from rich.traceback import install
from rich import print
install()
class Cliente():
    def __init__(self,endereço):
        self.endereço = endereço
        self.contas: list = []
    def realizar_transacao(self, conta: 'Conta', transacao: 'Transaçao') -> None:
        transacao.registar(conta)

    def adicionar_conta(self,conta):
        self.contas.append(conta)
        
class PessoaFisica(Cliente):
    def __init__(self, cpf,Nome,data_nascimento,endereço):
        super().__init__(endereço)
        self._cpf = cpf
        self._nome = Nome
        self._data_nascimento = data_nascimento

class Conta():
    def __init__(self,numero,cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
    @classmethod
    def nova_conta(cls,cliente,numero):
        return cls(numero,cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico

    def Sacar(self,valor):
        if valor <=0:
            print(f"[red]Impossivel sacar valor de {valor}[/]")
        elif valor > self.saldo:
            print(f"[red]Valor de: R${valor} ultrapassou o valor em conta.[/]")
        else:
            self._saldo -= valor
            return self._saldo
        return False

    def Depositar(self,valor):
        if valor <= 0 :
            print(f"[red]Nao foi possivel Depositar o valor de R${valor} [/]")
        elif valor > 0 :
            self._saldo = self.saldo + valor
            print(f"[green]Deposito de R${valor} feito com sucesso! [/]")
        else:
            return False

class ContaCorrente(Conta):
    def __init__(self,numero,cliente,limite=500,limite_saques=3):
        super().__init__(numero,cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def Sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == "Saque"])
        excedeu_limite_saques = numero_saques >= self.limite_saques
        excedeu_saldo = valor > (self.saldo + self.limite)

        if excedeu_saldo:
                print("[red]Falha: Saldo insuficiente, mesmo com o limite.[/]")
        elif excedeu_limite_saques:
                print("[red]Falha: Limite de saques diários atingido.[/]")
        else:
            return super().Sacar(valor)
        
        return False
    
class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),})

class Transaçao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    @abstractmethod
    def registar(self,conta):
        pass

class Saque(Transaçao):
    def __init__(self, valor):
        self._valor = valor
    @property
    def valor(self):
        return self._valor

    def registar(self, conta):
        if conta.Sacar(self.valor):
            conta.historico.adicionar_transacao(self)

class Deposito(Transaçao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registar(self, conta):
        if conta.Depositar(self.valor):
            conta.historico.adicionar_transacao(self)

def leiaint(n):
    while True:
        try:
            valor = int(input(n))
            return valor
        except (ValueError,TypeError):
            print("[red]Porfavor digite um numero inteiro valido[/]")
        except KeyboardInterrupt:
            print("[red]Usuario descediu nao informa um numero[/]")
            return 6

def escreva(txt):
    print("-=-"*10)
    print(f"[green]{txt}[/]".center(37))
    print("-=-"*10)

def menu(lista):
    escreva("MENU PRINCIPAL")
    c = 1
    for item in lista:
        print(f"{c} - {item} ")
        c+=1
    print()
    opçao = leiaint("Sua opçao -> ")
    return opçao 

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cli for cli in clientes if cli._cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("[red]Cliente não possui contas cadastradas.[/]")
        return None
    return cliente.contas[0]

clientes = []
contas = []

while True:
    resultado = menu(["CRIAR USUARIO ","CRIAR CONTA","DEPOSITAR","SACAR","EXTRATO","SAIR"])

    if resultado == 1 : 
        cpf = input("CPF (somente números): ")
        if filtrar_cliente(cpf, clientes):
            print("[red]Erro: CPF já cadastrado.[/]")
        else:
            nome = input("Nome: ")
            data = input("Nascimento (dd/mm/aaaa): ")
            end = input("Endereço: ")
            clientes.append(PessoaFisica(cpf, nome, data, end))
            print("[green]Usuário criado com sucesso![/]")  

    elif resultado == 2:
        cpf = input("CPF do dono da conta: ")
        cliente_encontrado = filtrar_cliente(cpf, clientes)
        if cliente_encontrado:
            numero_conta = len(contas) + 1
            conta = ContaCorrente.nova_conta(cliente_encontrado, numero_conta)
            contas.append(conta)
            cliente_encontrado.adicionar_conta(conta)
            if isinstance(cliente_encontrado, PessoaFisica):
                print(f"[green]Conta {numero_conta} criada para {cliente_encontrado._nome}![/]")
            else:
                print(f"[green]Conta {numero_conta} criada![/]")
        else:
            print("[red]Erro: Usuário não encontrado.[/]")

    elif resultado == 3:
        cpf = input("CPF: ")
        cliente = filtrar_cliente(cpf, clientes)
        if cliente:
            valor = float(input("Valor do depósito: "))
            conta = recuperar_conta_cliente(cliente)
            if conta:
                transacao = Deposito(valor)
                cliente.realizar_transacao(conta, transacao)
        else:
            print("[red]Erro: Cliente não encontrado.[/]")

    elif resultado == 4:
        cpf = input("CPF: ")
        cliente = filtrar_cliente(cpf, clientes)
        if cliente:
            valor = float(input("Valor do saque: "))
            conta = recuperar_conta_cliente(cliente)
            if conta:
                transacao = Saque(valor)
                cliente.realizar_transacao(conta, transacao)

    elif resultado == 5:
        cpf = input("CPF: ")
        cliente = filtrar_cliente(cpf, clientes)
        if cliente:
            conta = recuperar_conta_cliente(cliente)
            if conta:
                escreva("EXTRATO")
                transacoes = conta.historico.transacoes
                if not transacoes:
                    print("Não houve movimentações.")
                else:
                    for t in transacoes:
                        print(f"{t['data']} | {t['tipo']}: R${t['valor']:.2f}")
                print(f"\n[bold]Saldo atual: R${conta.saldo:.2f}[/]")
    
    if resultado == 6:
        break
