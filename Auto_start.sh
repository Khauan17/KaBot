#!/bin/bash

while true; do
  echo "🔁 Iniciando o bot por 4 horas..."
  python3 main.py
  echo "⏳ Esperando 20h para iniciar novamente..."
  sleep 20h
done
