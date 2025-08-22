from abc import ABC, abstractmethod
from datetime import datetime, date

## Interface para transacoes
class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    
    @abstractmethod
    def registrar(self, conta):
        pass

## Classe Deposito
class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    valor = property(lambda self: self._valor)
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

## Classe Saque
class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    valor = property(lambda self: self._valor)
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

## Classe historico transacoes
class Historico:
    def __init__(self):
        self._transacoes = []
    transacoes = property(lambda self: self._transacoes)
    def adicionar_transacao(self, transacao):
        self._transacoes.append(transacao)

## Classe Conta
class Conta:
    def __init__(self, numero, agencia, cliente):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = agencia
        self._cliente = cliente
        self._historico = Historico()
    
## Propriedades para encapsulamento de atributos privados(read only)
    saldo = property(lambda self: self._saldo)
    numero = property(lambda self: self._numero)
    agencia = property(lambda self: self._agencia)
    cliente = property(lambda self: self._cliente)
    historico = property(lambda self: self._historico)
    
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, "0001", cliente)
    def sacar(self, valor):
        if valor <= 0:
            print("Valor deve ser positivo!")
            return False
        if valor > self.saldo:
            print("Saldo insuficiente!")
            return False
        self._saldo -= valor
        return True
    def depositar(self, valor):
        if valor <= 0:
            print("Valor deve ser positivo!")
            return False
        self._saldo += valor
        return True

## Classe ContaCorrente
class ContaCorrente(Conta):
    def __init__(self, numero, agencia, cliente, limite=500.0, limite_saques=3):
        super().__init__(numero, agencia, cliente)
        self._limite = limite
        self._limite_saques = limite_saques
        self._saques_hoje = 0
        self._data_ultimo_saque = None
    limite = property(lambda self: self._limite)
    limite_saques = property(lambda self: self._limite_saques)
    def sacar(self, valor):
        hoje = date.today()
        if self._data_ultimo_saque != hoje:
            self._saques_hoje = 0
            self._data_ultimo_saque = hoje
        if valor > self.limite:
            print(f"Limite por saque: R$ {self.limite:.2f}")
            return False
        if self._saques_hoje >= self.limite_saques:
            print(f"Limite de saques diários atingido. ({self.limite_saques} saques/dia)")
            return False
        sucesso = super().sacar(valor)
        if sucesso:
            self._saques_hoje += 1
            print(f"Saques restantes hoje: {self.limite_saques - self._saques_hoje}")
        return sucesso

## Classe Cliente
class Cliente:
    def __init__(self, endereco):
        self._endereco = endereco
        self._contas = []
    endereco = property(lambda self: self._endereco)
    contas = property(lambda self: self._contas)
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
    def adicionar_conta(self, conta):
        self._contas.append(conta)

## Classe PessoaFisica
class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento
    cpf = property(lambda self: self._cpf)
    nome = property(lambda self: self._nome)
    data_nascimento = property(lambda self: self._data_nascimento)

## Validar cpf, nome e verificar se a idade do usuario e valida
def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))
    return len(cpf) == 11 and cpf != cpf[0] * 11
def validar_nome(nome):
    return (all(letra.isalpha() or letra.isspace() for letra in nome) 
            and len(nome.split()) >= 2)
def validar_data(data):
    try:
        data_nasc = datetime.strptime(data, '%d-%m-%Y')
        hoje = datetime.now()
        idade = hoje.year - data_nasc.year
        if (hoje.month, hoje.day) < (data_nasc.month, data_nasc.day):
            idade -= 1
        return 18 <= idade <= 100
    except:
        return False

## Cadastrar usuario
def criar_usuario():
    print("\n=== Cadastro de Novo Usuário ===")
    while True:
        cpf = input("Digite seu CPF: ")
        if validar_cpf(cpf):
            cpf = ''.join(filter(str.isdigit, cpf))
            cpf_existe = any(usuario.cpf == cpf for usuario in usuarios)
            if cpf_existe:
                print("CPF já cadastrado.")
                return
            else:
                break
        else:
            print("CPF inválido.")
    while True:
        nome = input("Nome completo: ").strip()
        if validar_nome(nome):
            break
        print("Nome inválido.")
    while True:
        data_nasc = input("Data de nascimento (dd-mm-aaaa): ")
        if validar_data(data_nasc):
            data_nasc = datetime.strptime(data_nasc, '%d-%m-%Y').date()
            break
        print("Data inválida.")
    endereco = input("Endereço (Rua, Nº - Bairro - Cidade/UF): ")
    novo_usuario = PessoaFisica(cpf, nome.title(), data_nasc, endereco)
    usuarios.append(novo_usuario)
    print("Usuário cadastrado com sucesso.")

## Criar nova conta
def criar_conta():
    if not usuarios:
        print("Cadastre um usuário primeiro.")
        return
    print("\n=== Nova Conta Bancária ===")
    while True:
        cpf = input("Digite o CPF do seu usuário: ")
        if validar_cpf(cpf):
            cpf = ''.join(filter(str.isdigit, cpf))
            break
        print("CPF inválido.")
    usuario_encontrado = None
    for usuario in usuarios:
        if usuario.cpf == cpf:
            usuario_encontrado = usuario
            break
    if usuario_encontrado:
        numero_conta = len(contas) + 1
        nova_conta = ContaCorrente.nova_conta(usuario_encontrado, numero_conta)
        usuario_encontrado.adicionar_conta(nova_conta)
        contas.append(nova_conta)
        print(f"Conta criada! Ag: 0001, C/C: {nova_conta.numero}")
    else:
        print("Usuário não encontrado!")

## Selecionar conta
def selecionar_conta():
    if not contas:
        print("Nenhuma conta disponível! Crie uma conta primeiro.")
        return None
    if len(contas) == 1:
        return contas[0]
    print("\n--- Contas Disponíveis ---")
    for i in range(len(contas)):
        conta = contas[i]
        print(f"{i+1}. Ag: {conta.agencia} C/C: {conta.numero} - {conta.cliente.nome}")
    try:
        escolha = int(input("Selecione uma conta (número): ")) - 1
        if 0 <= escolha < len(contas):
            return contas[escolha]
        else:
            print("Opção inválida!")
            return None
    except:
        print("Digite um número válido!")
        return None

## Deposito
def depositar():
    conta = selecionar_conta()
    if not conta:
        return
    try:
        valor = float(input("Valor a depositar: R$ "))
        if valor > 0:
            transacao = Deposito(valor)
            conta.cliente.realizar_transacao(conta, transacao)
            print("Depósito realizado com sucesso!")
        else:
            print("Valor deve ser positivo!")
    except:
        print("Valor inválido! Digite apenas números.")

## Saque
def sacar():
    conta = selecionar_conta()
    if not conta:
        return
    try:
        valor = float(input("Valor a sacar: R$ "))
        if valor > 0:
            transacao = Saque(valor)
            conta.cliente.realizar_transacao(conta, transacao)
        else:
            print("Valor deve ser positivo.")
    except:
        print("Valor inválido.")

## Extrato
def mostrar_extrato():
    conta = selecionar_conta()
    if not conta:
        return
    print("\n" + "="*50)
    print("                 EXTRATO BANCÁRIO")
    print("="*50)
    print(f"Titular: {conta.cliente.nome}")
    print(f"Ag: {conta.agencia}  C/C: {conta.numero}")
    print("-"*50)
    if not conta.historico.transacoes:
        print("Nenhuma movimentação encontrada.")
    else:
        for transacao in conta.historico.transacoes:
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            if isinstance(transacao, Deposito):
                print(f"[{timestamp}] Depósito: +R$ {transacao.valor:.2f}")
            elif isinstance(transacao, Saque):
                print(f"[{timestamp}] Saque: -R$ {transacao.valor:.2f}")
    print("-"*50)
    print(f"SALDO ATUAL: R$ {conta.saldo:.2f}")
    print("="*50)

## Listar todas as contas
def listar_contas():
    if not contas:
        print("Nenhuma conta cadastrada!")
        return
    print("\n=== CONTAS CADASTRADAS ===")
    for conta in contas:
        print(f"Ag: {conta.agencia} | C/C: {conta.numero} | "
            f"Titular: {conta.cliente.nome} | Saldo: R$ {conta.saldo:.2f}")

usuarios = []
contas = []

while True:
    print("\n" + "="*30)
    print("         MENU PRINCIPAL")
    print("="*30)
    print("1. Cadastrar Usuário")
    print("2. Criar Conta")
    print("3. Depositar")
    print("4. Sacar")
    print("5. Extrato")
    print("6. Listar Contas")
    print("7. Sair")
    print("="*30)
    opcao = input("Escolha uma opção (1-7): ")

    if opcao == "1":
        criar_usuario()
    elif opcao == "2":
        criar_conta()
    elif opcao == "3":
        depositar()
    elif opcao == "4":
        sacar()
    elif opcao == "5":
        mostrar_extrato()
    elif opcao == "6":
        listar_contas()
    elif opcao == "7":
        print("Obrigado por usar nosso banco. Até logo!")
        break
    else:
        print("Opção inválida. Digite um número de 1 a 7.")