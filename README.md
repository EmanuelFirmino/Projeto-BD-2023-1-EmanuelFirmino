# Sistema de Avaliação de Disciplinas e Docentes UnB - [Projeto Banco de Dados 2023/1]

# Tecnologias

* Python Flask
* MariaDB

# Intruções para execução

1. Fazer download e instalação das dependências:

    * `pip3 install -r requirements.txt`

2. Criar arquivo 'config.py' na pasta 'src' com as suas credenciais do banco de dados (MariaDB) no seguinte formato:

    * ``` # MariaDB info and credentials

        HOST 	 = <HOST_UTILIZADO [PADRÃO: 127.0.0.1]>
        USER 	 = <NOME_DE_USUÁRIO>
        PASSWORD =  <SENHA> 
        DATABASE = 'UNBSystem'

        SECRET_KEY = <UMA_SECRET_KEY [String qualquer]>

        USUARIO = 1
        PROFESSOR = 2
        DISCIPLINA = 3 ```

3. Iniciar a execução do MariaDB na porta 3306 [Linux]:

    * `systemctl start mariadb`

4. Alimentar o banco de dados (Certifique-se de estar na pasta 'src'):

    * `python3 app.py --feed`

    * O processo pode levar alguns minutos

5. Executar a aplicação web:

    * `python3 app.py --run`

6. A aplicação estará sendo executada em:

    * `http://localhost:5000`


