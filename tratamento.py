from database.queries import buscar_dados_magento
import pandas as pd
from pathlib import Path 

filtro_Eventos_Prime = [48133]
 
dados = buscar_dados_magento(filtro_Eventos_Prime)

colums = ["N. Peito", "Local", "SKU DO EVENTO ", "ID Evento", "Evento", 
          "Local Inscrição", "Balcão", "Protocolo", "ID Inscrição", "Data Evento", 
          "Data Pedido", "Status Pedido", "Status Confirmado", "Valor", "Modalidade", 
          "Modalidade Ajustada", "Categoria", "Assinante", "Pelotão", "ID Usuario", 
          "Nome inscrição", "Idade", "E-mail", "TELEFONE", "Documento", "Sexo", "Estado", 
          "Cidade", "Personalização", "Tamanho Camiseta", "Produtos", "Cupom", "Etiqueta", 
          "Classificacao Cupom"]


df = pd.DataFrame(dados, columns=colums)

valores_remover_Etiqueta = ["cortesia","corteisa","cortesias","grupos","grupos","company","teste","testes"]
valores_remover_Cupom = ["cortesia","grupos","grupo","teste","testes"]
valores_remover_Email = ["@nortemkt.com","@ativo.com","@cscdoesporte.com","@test.com","@teste","teste","testes","grupo","grupos"]
valores_remover_Categoria = ["cortesia","cortesias","grupos","company","grupo","saude corporativa","corporativa","patrocinador","teste","testes"]
valores_remover_Evento = ["cortesia","cortesias","grupos","grupo","teste","testes"]


# Remove Grupos e Cortesias
df = df[~df["Etiqueta"].str.lower().str.contains("|".join(valores_remover_Etiqueta))]
df = df[~df["Cupom"].str.lower().str.contains("|".join(valores_remover_Cupom))]
#df = df[~df["Cupom"].astype(str).str.strip().str.lower().str.startswith("gr", na=False)]
df = df[~df["E-mail"].str.lower().str.contains("|".join(valores_remover_Email))]
df = df[~df["Categoria"].str.lower().str.contains("|".join(valores_remover_Categoria))]
df = df[~df["Evento"].str.lower().str.contains("|".join(valores_remover_Evento))]

df["Estado"] = df["Estado"].str.strip()
df["Estado"] = df["Estado"].replace({
    "Acre": "AC",
    "Alagoas": "AL",
    "Amapá": "AP",
    "Amazonas": "AM",
    "Bahia": "BA",
    "Ceará": "CE",
    "Distrito Federal": "DF",
    "Espírito Santo": "ES",
    "Goiás": "GO",
    "Maranhão": "MA",
    "Mato Grosso": "MT",
    "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG",
    "Pará": "PA",
    "Paraíba": "PB",
    "Paraná": "PR",
    "Pernambuco": "PE",
    "Piauí": "PI",
    "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS",
    "Rondônia": "RO",
    "Roraima": "RR",
    "Santa Catarina": "SC",
    "São Paulo": "SP",
    "Sergipe": "SE",
    "Tocantins": "TO"
})            


# Apagar as linhas de Local Inscrição e Balcão que contém qualquer valor
df = df[df["Local Inscrição"].isna()]
df = df[df["Balcão"].isna()]

# Salva o arquivo tratado em Excel no diretório de Downloads
download_path = Path.home() / "Downloads" / 'tratamento.xlsx'
df.to_excel(download_path, index=False)
print(f"Arquivo salvo em: {download_path}") 

print(len(df))
print(df.tail(10))