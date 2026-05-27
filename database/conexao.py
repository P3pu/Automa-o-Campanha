"""
database/conexao.py
-------------------
Responsabilidade única: abrir e devolver conexões com os dois bancos.

Regra de negócio implícita:
  - Existem DOIS sistemas de origem separados:
      • Magento  → plataforma "Running Land" (e-commerce)
      • Ativo    → plataforma "Ativo.com"    (marketplace externo)
  - As credenciais são carregadas exclusivamente de variáveis de ambiente
    (.env via python-dotenv), nunca hard-coded no código.
  - O banco Ativo não expõe porta configurável; usa a porta padrão do MySQL (3306).
"""

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def conectar_bd_magento():
    """
    Abre e devolve uma conexão com o banco Magento (Running Land).
    O chamador é responsável por fechar a conexão após o uso.
    """
    print("[BD] Conectando ao banco Magento (Running Land)...")
    conn = mysql.connector.connect(
    host = os.getenv('DB_MAGENTO_HOST'),
    user = os.getenv('DB_MAGENTO_USER'),
    port=os.getenv("DB_MAGENTO_PORT", "3306"),
    password = os.getenv('DB_MAGENTO_PASSWORD'),
    database = os.getenv('DB_MAGENTO_DATABASE')
    )
    print("[BD] Conexão Magento estabelecida.")
    return conn


def conectar_bd_ativo():
    """
    Abre e devolve uma conexão com o banco Ativo (Ativo.com).
    O chamador é responsável por fechar a conexão após o uso.
    """
    print("[BD] Conectando ao banco Ativo (Ativo.com)...")
    conn = mysql.connector.connect(
        host=os.getenv("DB_ATIVO_HOST"),
        user=os.getenv("DB_ATIVO_USER"),
        password=os.getenv("DB_ATIVO_PASSWORD"),
        database=os.getenv("DB_ATIVO_DATABASE"),
    )
    print("[BD] Conexão Ativo estabelecida.")
    return conn