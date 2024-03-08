import textwrap
import os
import time
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

LIMITE_VALOR = 500
LIMITE_SAQUE = 3

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

    def __str__(self):
        str = f"""
        \033[FNome: {self.nome}
        Data de Nascimento: {self.data_nascimento}
        CPF: {self.cpf}""" 
        return textwrap.dedent(str)

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

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

    def sacar(self, valor):
        saldo = self.saldo

        if valor > saldo:
            limpar_print_time("Operação falhou! Você não tem saldo suficiente.")
        elif valor > 0:
            self._saldo -= valor
            limpar_print_time("Saque realizado com sucesso!")
            return True
        else:
            limpar_print_time("Operação falhou! O valor informado é inválido.")
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            limpar_print_time("Depósito realizado com sucesso!")
        else:
            limpar_print_time("Operação falhou! O valor informado é inválido.")
            return False
        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente):
        super().__init__(numero, cliente)
        self._limite = LIMITE_VALOR
        self._limite_saques = LIMITE_SAQUE

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            limpar_print_time("Operação falhou! O valor do saque excede o limite.")
        elif excedeu_saques:
            limpar_print_time("Operação falhou! Número máximo de saques excedido.")
        else:
            return super().sacar(valor)
        return False

    def __str__(self):
        str = f"""
            \033[FAgência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}"""
        return textwrap.dedent(str)

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def limpar_print_time(prompt):
    limpar_terminal()
    print(prompt)
    time.sleep(3)

def controle_input(prompt):
    while True:
        limpar_terminal()
        saida = input(prompt)
        if saida != "" and saida != "," and saida != ", ":
            return saida

def limpar_terminal():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def menu():
    limpar_terminal()
    menu = """
    \033[F================ MENU ================
    1 - Depositar
    2 - Sacar
    3 - Extrato
    4 - Criar Usuário
    5 - Criar Conta
    6 - Listar Contas
    7 - Sair\n
    Digite o número da sua opção: """
    return controle_input(textwrap.dedent(menu))

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        limpar_print_time("Cliente não possui conta!")
        return
    
    return cliente.contas[0]

def depositar(clientes):
    limpar_terminal()
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        return limpar_print_time("Cliente não encontrado!")

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)
    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        return limpar_print_time("Cliente não encontrado!")

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)
    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        return limpar_print_time("Cliente não encontrado!")

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    limpar_terminal()
    print("================ EXTRATO ================")
    transacoes = conta.historico.transacoes
    extrato = ""

    if not transacoes:
        limpar_terminal()
        print("Não foram realizadas movimentações.")
    else:
        for transacao in transacoes:
            extrato += f"Data: {transacao['data']} - {transacao['tipo']}: R$ {transacao['valor']:.2f}\n"

    print(extrato)
    print(f"Saldo: R$ {conta.saldo:.2f}")
    print("==========================================")
    input("\nAperte Enter para continuar")

def criar_cliente(clientes):
    limpar_terminal()
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        return limpar_print_time("O CPF já está cadastrado!")

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
    cliente = PessoaFisica(nome = nome, data_nascimento = data_nascimento, cpf = cpf, endereco = endereco)
    clientes.append(cliente)
    limpar_print_time("Cliente criado com sucesso!")

def criar_conta(numero_conta, clientes, contas):
    limpar_terminal()
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        return limpar_print_time("Cliente não encontrado!")

    nova_conta = ContaCorrente.nova_conta(cliente = cliente, numero = numero_conta)
    contas.append(nova_conta)
    cliente.contas.append(nova_conta)
    limpar_print_time("Conta criada com sucesso!")

def listar_contas(contas):
    if len(contas) == 0:
        limpar_print_time("Não há contas para listar.")
    else:
        for conta in contas:
            print("=" * 100)
            print(textwrap.dedent(str(conta)))
        input("\nAperte Enter para continuar")

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            limpar_terminal()
            depositar(clientes)

        elif opcao == "2":
            limpar_terminal()
            sacar(clientes)

        elif opcao == "3":
            limpar_terminal()
            exibir_extrato(clientes)

        elif opcao == "4":
            limpar_terminal()
            criar_cliente(clientes)

        elif opcao == "5":
            limpar_terminal()
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "6":
            limpar_terminal()
            listar_contas(contas)

        elif opcao == "7":
            break

        else:
            limpar_print_time("Operação inválida, por favor selecione novamente a operação desejada.")

main()