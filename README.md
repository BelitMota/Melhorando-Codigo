# Melhorando-Codigo
Reestruturação e organização de um código armador disponibilizado na aula de Programação Back-end Orientado a Objetos

## Organizando a Arquitetura de Pastas:

A arquitetura de pastas nada mais é do que uma organização e boa estruturação dos diretórios e arquivos originado para seu projeto.

- add pasta chamada "routes" referente as rotas "/" (endpoints)
- add pasta só pra armazenar coisas relacionadas ao banco (repositories)
- add um pasta ou arquivo somente para a organização dos filtros e validações (separada da rota), talvez por meio de classes e metodos?? (services)
- ver um outro lugar pra por o "cursor.execute", junto com seu return, ele parece meio jogado, por mais que seja referente ao metodo e a rota (tbm referente ao banco)
- talvez salvar o arquivo do banco em formato json e desse formato tratar-mos ele?
- baseando-se no "tarefas" que ele cria apenas uma lista comum, um array basico "tarefas = []", e posterior a isso, ele pega cada item pelo indice do array. Pode-se resolver isso utilizando uma lista de dicionários:
    tarefas = [
        {}
    ]

## Observações:
> Percebe-se que dentro de cada rota tem uma tonelada de funções/métodos de forma desorganizada e esquisito de ler e procurar. Além disso há códigos, que deveriam estar num arquivo especificado para tratar as coisas referente ao banco (UPDATE, CREATE, DELETE, READ), e pelo o que foi observado há códigos desse tipo dentro das proprias rotas.
