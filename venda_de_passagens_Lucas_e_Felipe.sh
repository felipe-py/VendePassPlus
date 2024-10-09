#!/bin/bash

echo "niciando VendePass."

# CD para a pasta do projeto. Como é a mesma fica aqui só para "caso tenha que mudar".
cd "$(dirname "$0")"

# Verifica se o Docker está instalado
if ! command -v docker &>/dev/null; then
	echo "O docker não está instalado."
	exit 1
fi

# Verifica se o Docker Compose está instalado
if ! command -v docker-compose &>/dev/null; then
	echo "Docker Compose não está instalado."
	exit 1
fi

# Cria e executa os containers com Docker Compose
docker-compose up --build -d

# echo "Containers do VendePass estão rodando. Use 'docker-compose ps' para verificar o status."
