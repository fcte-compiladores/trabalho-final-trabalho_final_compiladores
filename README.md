[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Hppw7Zh2)

# Compilador de ArnoldC 😎

**Título:** Compilador de ArnoldC

**Integrantes:**

| Nome                    | Matrícula   |
|-------------------------|-------------|
| Larissa de Jesus Vieira | 221022050   |

## Introdução
Este projeto consiste na implementação de um interpretador para um subconjunto da linguagem de programação [**ArnoldC**](https://banhawy.github.io/ArnoldC-Technical-Documentation/#main-method). 

ArnoldC é uma linguagem de programação esotérica onde todo o código é composto por citações famosas de filmes do ator Arnold Schwarzenegger.

O objetivo principal foi adaptar as estruturas que vimos na disciplina Compiladores 1, ministrada pelo Prof. Fábio Mendes, construindo um compilador em Python para executar programas simples em ArnoldC.

Os elementos abordados no trabalho são:
* **Estrutura Básica do Programa:** Todo programa começa com `IT'S SHOWTIME` e termina com `YOU HAVE BEEN TERMINATED`.
* **Definição de Variáveis:** Variáveis são declaradas usando `HEY CHRISTMAS TREE <nome_variavel> YOU SET US UP <valor_inicial>`.
* **Atribuição de Variáveis:** Variáveis recebem valores com `GET TO THE CHOPPER <nome_variavel> HERE IS MY INVITATION <expressão> ENOUGH TALK`.
* **Impressão:** Os comandos de print são realizados com `TALK TO THE HAND <expressão>`.
* **Operações Aritméticas e Lógicas:**
    * Adição: `GET UP <operando>`
    * Subtração: `GET DOWN <operando>`
    * Multiplicação: `YOU'RE FIRED <operando>`
    * Divisão: `HE HAD TO SPLIT <operando>`
    * Ou: `OR NO RAIN <operando>`
    * E: `KNOCK KNOCK <operando>`
* **Definição de Métodos:** Métodos são definidos com `LISTEN TO ME VERY CAREFULLY <nome_metodo> [parâmetros...] [GIVE THESE PEOPLE AIR] <bloco_de_código> HASTA LA VISTA, BABY`. `GIVE THESE PEOPLE AIR` indica que o método tem um retorno.
* **Parâmetros de Métodos:** São declarados com `I NEED YOUR CLOTHES YOUR BOOTS AND YOUR MOTORCYCLE <nome_parametro>`.
* **Chamada de Métodos:** `GET YOUR ASS TO MARS <variavel_resultado> DO IT NOW <nome_metodo> [argumentos...]`.
* **Retorno de Método:** `I'LL BE BACK <expressão>`.
* **If:** `BECAUSE I'M GOING TO SAY PLEASE <condição> [bloco_if] [BULLSHIT [bloco_else]] YOU HAVE NO RESPECT FOR LOGIC`
* **While:** `STICK AROUND <condição> [bloco_loop] CHILL`

## Instalação e Execução
**1) Pré-requisitos:**
* Python 3.10 ou superior
* pip (gerenciador de pacotes Python)

**2) Clonar o Repositório:**
```bash
git clone https://github.com/fcte-compiladores/trabalho-final-trabalho_final_compiladores.git
cd trabalho-final-trabalho_final_compiladores
```
**3) Criar e Ativar Ambiente Virtual:**
```bash
python3 -m venv .venv
source .venv/bin/activate # No Linux/macOS
.venv\Scripts\activate # No Windows
```
**4) Instalar Dependências:**
```bash
pip install -r requirements.txt
```
**5) Executar o Compilador:**

Para executar um arquivo ArnoldC, use o comando *run*. 
No projeto já existem alguns exemplos de código ArnoldC na pasta *exemplos*, que podem ser executados como o comando abaixo.
```bash
python3 -m arnoldc run exemplos/decl_and_call_method.arnoldc
```

## Exemplos
A pasta [*exemplos*](exemplos), como já abordado, possui alguns exemplos simples de códigos ArnoldC para testes. Ao todo são sete, porém aqui trago apenas dois:

* helloworld.arnoldc
```
IT'S SHOWTIME
TALK TO THE HAND "Hello, World!"
YOU HAVE BEEN TERMINATED
```

* while.arnoldc
```
IT'S SHOWTIME
HEY CHRISTMAS TREE cnt YOU SET US UP 3

STICK AROUND cnt
    TALK TO THE HAND "Estou dentro do loop! Contador: "
    TALK TO THE HAND cnt
    GET TO THE CHOPPER cnt
    HERE IS MY INVITATION cnt
    GET DOWN 1
    ENOUGH TALK
CHILL

TALK TO THE HAND "Final do loop."
YOU HAVE BEEN TERMINATED
```

## Referências
⚠️ Esse trabalho é uma adaptação do projeto Lox do Prof. Fábio Mendes, que foi visto em sala de aula durante o semestre de 2025/2. Muitas estruturas e/ou arquivos foram reutilizados.

* Repositório do Professor Fábio (https://github.com/fcte-compiladores/2025-1)
* Crafting Interpreters, Robert Nystrom, 2015-2021. (https://craftinginterpreters.com/)
* BANHAWY, Mohamed. ArnoldC Technical Documentation. Disponível em: <https://banhawy.github.io/ArnoldC-Technical-Documentation/#main-method>. Acesso em: 20 jul. 2025.
* ESOLANGS. ArnoldC. Disponível em: <https://esolangs.org/wiki/ArnoldC>. Acesso em: 20 jul. 2025.
* HARTIKKA, Lauri. ArnoldC. GitHub. Disponível em: <https://github.com/lhartikk/ArnoldC>. Acesso em: 20 jul. 2025.

Para o entendimento da linguagem ArnoldC, utilizei o site [ArnoldC Documentation](https://banhawy.github.io/ArnoldC-Technical-Documentation/#main-method) e o [repositório oficial do ArnoldC](https://github.com/lhartikk/ArnoldC)

## Estrutura do código
O projeto está organizado na seguinte estrutura de diretórios e arquivos:
```
.
├── arnoldc/
│   ├── __init__.py          
│   ├── __main__.py          
│   ├── arnoldc_ast.py       # Definições dos nós da Abstract Syntax Tree (AST).
│   ├── cli.py               # Interface de linha de comando (CLI) usando argparse.
│   ├── ctx.py               # Gerenciamento do contexto de execução e escopos de variáveis.
│   ├── errors.py            # Definições de exceções customizadas para erros de ArnoldC.
│   ├── grammar.lark         # Definição da gramática de ArnoldC para o Lark. Responsável pela análise léxica e sintática (produz a CST).
│   ├── parser.py            # Integra a gramática Lark e fornece funções para tokenização (lex), parsing para CST (parse_cst) e AST (parse).
│   ├── runtime.py           # Contém a lógica principal para a avaliação da AST.
│   ├── transformer.py       # Classe Transformer do Lark que converte a CST na AST definida em `arnoldc_ast.py`.
│   └── node.py              # Definição de uma classe base para nós da AST ou para o sistema de validação.
├── exemplos/                # Pasta contendo alguns programas de exemplo em ArnoldC.
│   ├── helloworld.arnoldc
│   ├── decl_and_call_method.arnoldc
│   └── ... (outros exemplos)
├── .gitgnore               
├── requirements.txt         # Gerenciamento de dependências do projeto (no lugar do pyproject.toml).
└── README.md                 
```

## Bugs/Limitações/problemas conhecidos
* **Testes:** Infelizmente, não foram implementados testes unitários para verificar a correção de módulos individuais. Embora existam arquivos de exemplo na pasta `exemplos/`, ainda são **necessários mais casos de teste** abrangentes para garantir o funcionamento pleno e robusto do interpretador/compilador.
* **Tipagem:** ArnoldC é dinamicamente tipado. O compilador atual não realiza verificação de tipos em tempo de compilação, erros desse tipo (ex: somar um número com uma string) são capturados apenas em tempo de execução.
* **Funcionalidades Não Implementadas:** O projeto cobre um subconjunto da linguagem ArnoldC. Funcionalidades mais avançadas (se existirem na especificação completa e não foram implementadas) não estão presentes.

**Melhorias Futuras Potenciais:**

* Implementar todas as operações e construções da especificação completa do ArnoldC.
* Melhorar a detecção e o relato de erros semânticos antes da execução.
* Desenvolver um conjunto de testes mais robusto para todas as funcionalidades.
