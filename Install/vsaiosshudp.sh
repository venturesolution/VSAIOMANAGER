#!/bin/bash

# ##########################################################
# Script de Instalação do BadVPN - UDP Gateway
# Autor: @fermandoangeli 
# GitHub: @venturesolution (vsaiossh)
# Telegram: @vsaiossh
# Cientista de dados e Bacharelado em Tecnologia da Informação pela Universidade de Havard
# ##########################################################

# Função para exibir mensagens de erro e sair do script
function erro {
    echo "Erro: $1"
    exit 1
}

# Função para verificar a arquitetura do sistema
function verificar_arquitetura {
    ARCH=$(uname -m)
    case $ARCH in
        x86_64)
            echo "Arquitetura: x86_64 (64-bit)"
            BADVPN_REPO="https://github.com/ambrop72/badvpn.git"
            ;;
        aarch64)
            echo "Arquitetura: aarch64 (ARM 64-bit)"
            BADVPN_REPO="https://github.com/ambrop72/badvpn.git"
            ;;
        *)
            erro "Arquitetura não suportada: $ARCH"
            ;;
    esac
}

# 1. Atualizando os repositórios e instalando as dependências necessárias.
echo "Atualizando os repositórios e instalando dependências..."
sudo apt update && sudo apt install -y build-essential cmake git || erro "Falha ao instalar dependências."

# 2. Verificando a arquitetura do sistema e configurando o repositório apropriado.
verificar_arquitetura

# 3. Baixando o código-fonte do BadVPN do repositório adequado
echo "Baixando o código-fonte do BadVPN..."
git clone $BADVPN_REPO || erro "Falha ao clonar o repositório BadVPN."
cd badvpn || erro "Falha ao acessar o diretório badvpn."

# 4. Configurando a compilação para incluir o UDP Gateway
echo "Configurando a compilação para incluir o UDP Gateway..."
cmake -DCMAKE_INSTALL_PREFIX=/usr -DBUILD_NOTHING_BY_DEFAULT=1 -DBUILD_UDPGW=1 . || erro "Falha ao configurar a compilação."

# 5. Compilando o programa (isso pode demorar um pouco dependendo do seu hardware)
echo "Compilando o BadVPN (isso pode levar alguns minutos, dependendo do seu hardware)..."
make -j$(nproc) || erro "Falha na compilação do BadVPN."

# 6. Instalando o binário compilado
echo "Instalando o BadVPN..."
sudo make install || erro "Falha na instalação do BadVPN."

# Mensagem final de sucesso
echo "BadVPN UDP Gateway instalado com sucesso!"

# ##########################################################
# Fim do script
# ##########################################################