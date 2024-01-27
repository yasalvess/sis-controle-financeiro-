import sqlite3
import pandas as pd
import os
from prettytable import PrettyTable

#CRIA BANCO DE DADOS

conexao = sqlite3.connect('sisBd.db')

#INSTANCIAR BANCO DE DADOS------------------------------------------------

conexaoCursor = conexao.cursor()

try:
    
    #CRIAR TABELA DESPESA------------------------------------------------
    
    conexaoCursor.execute('''
    CREATE TABLE IF NOT EXISTS despesa(
                        idDespesa INTEGER PRIMARY KEY AUTOINCREMENT,
                        nomeDespesa TEXT NOT NULL,
                        tipoDespesa TEXT CHECK(tipoDespesa IN('Fixa', 'Variavel')) NOT NULL,  
                        qtdXDespesa INTEGER NOT NULL,
                        valorParcela REAL NOT NULL,    
                        valorTotal REAL NOT NULL
                        )
        
    
    ''')

    #CRIAR TABELA DE METAS------------------------------------------------
    conexaoCursor.execute('''
    CREATE TABLE IF NOT EXISTS metas(
                        idMetas INTEGER PRIMARY KEY AUTOINCREMENT,
                        nomeMeta TEXT NOT NULL,
                        tempoMeta INTEGER NOT NULL,
                        valorMeta INTEGER NOT NULL
                        )
    ''')
    
    conexao.commit()
    
except Exception as e:
    print(f'Erro ao criar banco de dados: {str(e)}')

#LIMPAR TERMINAL------------------------------------------------
def limpaTerminal():
    os.system('cls')
    
#CADASTRAR DESPESA------------------------------------------------

def cadastrarDespesa(nomeDespesa, tipoDespesa, qtdXDespesa, valorParcela, valorTotal):
    conexaoCursor.execute('INSERT INTO despesa(nomeDespesa, tipoDespesa, qtdXDespesa, valorParcela, valorTotal)'
                          'VALUES (?, ?, ?, ?, ?)',(nomeDespesa, tipoDespesa, qtdXDespesa, valorParcela, valorTotal))
    conexao.commit()
    
#CADASTRO DE METAS------------------------------------------------

def cadastrarMetas(nomeMeta, tempoMeta, valorMeta):
    conexaoCursor.execute('INSERT INTO metas(nomeMeta, tempoMeta, valorMeta)'
                          'VALUES (?, ?, ?)', (nomeMeta, tempoMeta, valorMeta))
    conexao.commit()
    

def exibirDespesas(despesa):
    if despesa is not None and not despesa.empty:
        tabela = PrettyTable()
        tabela.field_names = ["nomeDespesa", "tipoDespesa", "totalDespesa"]

        # Certifique-se de que o DataFrame tem as colunas necessárias
        if set(["nomeDespesa", "tipoDespesa", "totalDespesa"]).issubset(despesa.columns):
            for despesa in despesa.itertuples(index=False):
                tabela.add_row(despesa)
            print(tabela)
            print('DataFrame columns: {despesa.olumns}')
        else:
            return 'O DataFrame não tem as colunas necessárias para exibição!'
            print('DataFrame columns: {despesa.olumns}')
    else:
        return 'Não há despesas cadastradas! '


def calcularMediaEconomia(tempoMeta, valorMeta):
    media = valorMeta / tempoMeta if tempoMeta > 0 else 0
    #return "{:.1f}".format(media)
    return round(media, 1)

def valorTotalMetas(metas):
    if 'media_mensal' in metas.columns:
        valores_media_mensal = metas['media_mensal'].apply(lambda x: float(x.replace(',', '.')))
        valor_total_metas = sum(valores_media_mensal)
        return "{:.1f}".format(valor_total_metas).replace('.', ',')
    else:
        return 'A coluna "media_mensal" não está no df metas'

    
def exibirMetas(metas):
    if not metas.empty:
        tabela = PrettyTable()
        tabela.field_names = ["Nome", "Meses", "Valor", "Média"]  
        
        valores_media_mensal = []
        
        for metas in metas.itertuples(index=False):
            nomeMeta, tempoMeta, valorMeta = metas[1], metas[2], metas[3]
            media_mensal = calcularMediaEconomia(tempoMeta, valorMeta)
            valores_media_mensal.append(media_mensal)
            tabela.add_row([nomeMeta, tempoMeta, valorMeta, media_mensal])
     
        print(tabela)
            
        valor_total_metas = sum(valores_media_mensal)
        print(f'\nValor total a ser guardado por mês: {valor_total_metas}')
    else:
        print('Não há metas cadastradas!')
        
def despesaMensal():
    
    query = f"SELECT nomeDespesa, tipoDespesa, SUM(valorParcela) AS totalDespesa " \
            f"FROM despesa " \
            f"WHERE strftime('%Y-%m', date('now', 'localtime')) = strftime('%Y-%m', datetime('now', 'localtime')) " \
            f"GROUP BY nomeDespesa, tipoDespesa"
        
    despesa_mensal = pd.read_sql_query(query, conexao)
    
    df_despesa_mensal = pd.DataFrame({
        'nomeDespesa': despesa_mensal['nomeDespesa'],
        'tipoDespesa': despesa_mensal['tipoDespesa'],
        'totalDespesa': despesa_mensal['totalDespesa'],
    }) 
    
    result_exibicao = exibirDespesas(df_despesa_mensal)
    print(result_exibicao)
    
    valor_total = df_despesa_mensal['totalDespesa'].sum()
    
    print('\n+----------------------------------------+')
    print(f'|Valor total das despesas do mês: {valor_total}|')
    print('+----------------------------------------+')

def exibirMenu():
    print('\n')
    print('---------------------DESPESAS----------------------')
    print('|                                                 |')
    print('| [1] - CADASTRAR DESPESA                         |')
    print('| [2] - CADASTRAR METAS                           |')
    print('| [3] - EXIBIR DESPESAS                           |')
    print('| [4] - EXIBIR METAS                              |')
    print('| [5] - EXIBIR FATURA MENSAL                      |')
    print('|                                                 |')
    print('---------------------------------------------------')
    
if 'y' == 'y':
    while True:
        
        # Lendo os dados da tabela despesa

        dataFrameDespesa= pd.read_sql_query('SELECT * FROM despesa', conexao)
   
        # Lendo os dados da tabela metas
        dataFrameMetas = pd.read_sql_query('SELECT * FROM metas', conexao)
        
#        dataFrameFaturaMensal = pd.read_sql_query('SELECT * FROM metas', conexao)

        exibirMenu()
        
        operacao = input('\nEscolha uma oção: ')
        
        if operacao == '1':
            
            op = '1'
            
            while op == '1' or 'sim':
                limpaTerminal()
                
                print('Você escolheu cadastrar!\n')
                nomeDespesa = input('Nome: ').capitalize()
                tipoDespesa = input('Tipo: ')
                qtdXDespesa = int(input('Quantidades de parcelas: '))
                if (qtdXDespesa > 1):
                    valorParcela = (input('Digite o valor da parcela: '))
                valorTotal = (input('Digite o valor total: '))
                cadastrarDespesa(nomeDespesa, tipoDespesa, qtdXDespesa, valorParcela, valorTotal)
                op = input('Deseja cadastrar outra despesa? ')
                if op.lower != 'sim':
                    break
                else:
                    continue
            else:
                limpaTerminal()
                pass
        elif operacao == '2':
            
            op = '2'
            while op == '2' or 'sim':
                limpaTerminal()
                        
                limpaTerminal()
                print('Você escolheu a opção CADASTRAR METAS!')
                nomeMeta = input('Nome da meta: ')
                tempoMeta = int(input('Duração da meta: '))
                valorMeta = float(input('Valor da meta: '))
                cadastrarMetas(nomeMeta, tempoMeta, valorMeta)
                op = input('Deseja cadastrar outra meta? (Digite "sim" ou "nao"): ')
                if op.lower != 'sim':
                    break
                else:
                    continue
            else:
                limpaTerminal()
                pass

        elif operacao == '3':
            limpaTerminal()
            print('Você escolheu EXIBIR DESPESAS!')

            if not dataFrameDespesa.empty:
                print(dataFrameDespesa.to_markdown(index=False))
            else:
                print('Não há despesas cadastradas!')
            
        elif operacao == '4':
            limpaTerminal()
            print('Você escolheu EXIBIR METAS!')
            exibirMetas(dataFrameMetas)
            
        elif operacao == '5':
            limpaTerminal()
            print('Você escolheu EXIBIR FATURA MENSAL!')
            df_despesa_mensal = despesaMensal()
            print(df_despesa_mensal)
