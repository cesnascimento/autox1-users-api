# Usar uma imagem oficial do Python como base
FROM python:3.8

# Definir o diretório de trabalho no container
WORKDIR /code

# Copiar o arquivo de dependências e instalar os pacotes necessários
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante dos arquivos da aplicação para o container
COPY . /code/

# Copiar o script de entrada e torná-lo executável
COPY entrypoint.sh /code/
RUN chmod +x /code/entrypoint.sh

# Expõe a porta que o Django estará escutando
EXPOSE 8000

ENTRYPOINT ["sh", "/code/entrypoint.sh"]

# Comando para iniciar a aplicação Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
