from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field

PAGINA = Path(__file__).parent / "pagina.html"

DESCRICAO = """
API para **cadastrar, listar, atualizar e apagar** pontos turísticos do Acre,
cada um com sua localização (latitude e longitude).

**Como testar aqui:** clique em um endpoint, depois em **Try it out**, preencha os campos
e clique em **Execute**. O resultado aparece logo abaixo, com o *status code*
(200 deu certo, 201 criado, 204 apagado, 400 pedido com erro, 404 não encontrado).

Prefere uma tela com mapa? Abra a [página inicial](/).
"""

app = FastAPI(
    title="API Pontos Turísticos do Acre",
    description=DESCRICAO,
    version="2.0.0",
    openapi_tags=[{"name": "Pontos turísticos", "description": "Operações de CRUD sobre os pontos turísticos."}],
)


class Ponto(BaseModel):
    """Campos obrigatórios para cadastrar um ponto turístico."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "nome": "Parque Zoobotânico",
                    "cidade": "Rio Branco",
                    "descricao": "Área verde da UFAC com trilhas e fauna local.",
                    "latitude": -9.9556,
                    "longitude": -67.8700,
                }
            ]
        },
    )

    nome: str = Field(min_length=1)
    cidade: str = Field(min_length=1)
    descricao: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)      # ex.: -9.9556 (sul é negativo)
    longitude: float = Field(ge=-180, le=180)   # ex.: -67.8700 (oeste é negativo)


# Dados em memória (uma lista). Coordenadas APROXIMADAS: ajustem pelo mapa (editar e arrastar o pino).
pontos = [
    {"id": 1, "nome": "Palácio Rio Branco", "cidade": "Rio Branco",
     "descricao": "Antiga sede do governo, hoje museu e centro cultural.",
     "latitude": -9.9745, "longitude": -67.8075},
    {"id": 2, "nome": "Parque Zoobotânico da UFAC", "cidade": "Rio Branco",
     "descricao": "Área verde da universidade com trilhas e fauna local.",
     "latitude": -9.9556, "longitude": -67.8700},
    {"id": 3, "nome": "Casa de Chico Mendes", "cidade": "Xapuri",
     "descricao": "Casa onde viveu o seringueiro e ambientalista Chico Mendes.",
     "latitude": -10.6512, "longitude": -68.4975},
    {"id": 4, "nome": "Gameleira", "cidade": "Rio Branco",
     "descricao": "Árvore centenária às margens do Rio Acre que marca o local de fundação de Rio Branco, no calçadão histórico.",
     "latitude": -9.9780, "longitude": -67.8105},
    {"id": 5, "nome": "Museu da Borracha", "cidade": "Rio Branco",
     "descricao": "Museu em prédio histórico do centro, dedicado à história do ciclo da borracha no Acre.",
     "latitude": -9.9750, "longitude": -67.8100},
    {"id": 6, "nome": "Parque Ambiental Chico Mendes", "cidade": "Rio Branco",
     "descricao": "Fragmento de floresta urbana com trilhas e zoológico de fauna amazônica, na rodovia AC-40 (Vila Acre).",
     "latitude": -10.0250, "longitude": -67.8130},
    {"id": 7, "nome": "Museu Universitário da UFAC", "cidade": "Rio Branco",
     "descricao": "Museu da universidade, no campus-sede, com acervo ligado à história e à cultura acreana.",
     "latitude": -9.9575, "longitude": -67.8665},
    {"id": 8, "nome": "Memorial dos Autonomistas", "cidade": "Rio Branco",
     "descricao": "Memorial da Revolução Acreana que abriga a cripta de Plácido de Castro.",
     "latitude": -9.9725, "longitude": -67.8090},
    {"id": 9, "nome": "Catedral Nossa Senhora de Nazaré", "cidade": "Rio Branco",
     "descricao": "Catedral metropolitana no centro histórico de Rio Branco.",
     "latitude": -9.9735, "longitude": -67.8062},
    {"id": 10, "nome": "Parque Nacional da Serra do Divisor", "cidade": "Cruzeiro do Sul",
     "descricao": "Parque na fronteira com o Peru, com serras e floresta de grande biodiversidade. Pino no centro aproximado do parque.",
     "latitude": -8.1500, "longitude": -73.2500},
]
proximo_id = 11  # contador separado: não repete id depois de um DELETE


@app.exception_handler(RequestValidationError)
async def erro_validacao(request: Request, exc: RequestValidationError):
    # O FastAPI responde 422 por padrão; o trabalho pede 400.
    detalhes = [{"campo": str(e["loc"][-1]), "mensagem": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=400, content={"erro": "dados inválidos", "detalhes": detalhes})


def buscar(ponto_id: int):
    for p in pontos:
        if p["id"] == ponto_id:
            return p
    raise HTTPException(status_code=404, detail="ponto turístico não encontrado")


@app.get("/", include_in_schema=False)
def pagina_inicial():
    # Página com mapa que usa os endpoints abaixo (não conta como endpoint da API)
    return FileResponse(PAGINA)


@app.get("/pontos", tags=["Pontos turísticos"], summary="Lista todos os pontos")
def listar():
    return pontos


@app.get("/pontos/{ponto_id}", tags=["Pontos turísticos"], summary="Mostra um ponto pelo id",
         responses={404: {"description": "Ponto não encontrado"}})
def mostrar(ponto_id: int):
    return buscar(ponto_id)


@app.post("/pontos", status_code=201, tags=["Pontos turísticos"], summary="Cadastra um ponto novo",
          responses={400: {"description": "Falta algum campo obrigatório ou valor inválido"}})
def criar(ponto: Ponto):
    global proximo_id
    novo = {"id": proximo_id, **ponto.model_dump()}
    proximo_id += 1
    pontos.append(novo)
    return novo


@app.put("/pontos/{ponto_id}", tags=["Pontos turísticos"], summary="Atualiza um ponto",
         responses={400: {"description": "Falta algum campo obrigatório ou valor inválido"},
                    404: {"description": "Ponto não encontrado"}})
def atualizar(ponto_id: int, ponto: Ponto):
    existente = buscar(ponto_id)
    existente.update(ponto.model_dump())
    return existente


@app.delete("/pontos/{ponto_id}", status_code=204, tags=["Pontos turísticos"], summary="Apaga um ponto",
            responses={404: {"description": "Ponto não encontrado"}})
def apagar(ponto_id: int):
    pontos.remove(buscar(ponto_id))
    return Response(status_code=204)
