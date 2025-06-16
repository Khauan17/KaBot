#!/bin/bash

nohup python3 main.py > log.txt 2>&1 &
echo "✅ Bot iniciado manualmente e está rodando em segundo plano!"
