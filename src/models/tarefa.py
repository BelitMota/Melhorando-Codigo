
# Referencia
# "id": linha[0],
# "titulo": linha[1],
# "descricao": linha[2],
# "usuario": linha[3],
# "status": linha[4],
# "prazo": linha[5],
# "criado_em": linha[6],
# "concluido_em": linha[7]

class Tarefa:

# apenas os atributos
    def __init__(self,id:int,
                 titulo:str,
                 descricao:str,
                 usuario:str,
                 status:str,
                 prazo:str,
                 criado_em:str,
                 concluido_em:str) -> None:
        
        self.id = id
        self.titulo = titulo
        self.descricao = descricao
        self.usuario = usuario
        self.status = status
        self.prazo = prazo
        self.criado_em = criado_em
        self.concluido_em = concluido_em


    # metodos fundamentais
    @staticmethod
    def from_dict(dados:dict[str,str|int]) -> Tarefa | None:

        # validação basica
        if(dados is None):
            return None

        return Tarefa(
            id=dados["id"],
            titulo=dados["titulo"],
            descricao=dados["descricao"],
            usuario=dados["usuario"],
            status=dados["status"],
            prazo=dados["prazo"],
            criado_em=dados["criado_em"],
            concluido_em=dados["concluido_em"]
        )
        
    def to_dict(self) -> dict [str, str | int]:
         return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "usuario": self.usuario,
            "status": self.status,
            "prazo": self.prazo,
            "criado_em": self.criado_em,
            "concluido_em": self.concluido_em
        }


# criando uma "subclasse" para os status da tarefa
# object calistenics (renato augusto) -> cria classes pra separar as validações de forma mais organizada (por exemplo uma classe email que tem todas as suas validações dentro da mesma). 
# ai somente mudaria o tipo do objeto, mudando o tipo pra ser a classe.

class StatusTarefa:

    # OBS: letra maiuscula normalmente é uma constante, não é obrigatorio, mas comumente é
    PENDENTE = "PENDENTE"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"

    # obs: metodo estatico nao precisa de self
    @staticmethod
    def todos():
        return[
            StatusTarefa.PENDENTE,
            StatusTarefa.EM_ANDAMENTO,
            StatusTarefa.CONCLUIDA,
            StatusTarefa.CANCELADA,
        ]
    @staticmethod
    def normalizar(status:str | None) -> str | None:

        if(status is None):
            return None

        return status.strip().upper()
    
    # verifica se esta presente dentro desse vetor (falando se é verdadeiro ou falso)
    @staticmethod
    def eh_valido(status:str) -> bool:
        return(status in StatusTarefa.todos())