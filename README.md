# API Pontos Turísticos do Acre

API para cadastrar, listar, atualizar e apagar pontos turísticos do Acre, cada um com sua localização (latitude e longitude).
Trabalho de ARA0160 · Sistemas Distribuídos e Computação Paralela · Sistemas de Informação · Estácio UNIMETA.

## Integrantes
- EDUARDO ROGER MONTEIRO MENINI

## Tecnologias
- Back-end: Python 3.12, FastAPI, Uvicorn (dados guardados em memória)
- Página com mapa: HTML, CSS e JavaScript puro + Leaflet (mapa interativo) e OpenStreetMap (imagens do mapa). Não precisa de chave de API.

## Como rodar
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
A API sobe em http://localhost:8000.

- **http://localhost:8000**: página com mapa interativo para cadastrar, editar e apagar pontos (usa a própria API). Precisa de internet para carregar o mapa.
- **http://localhost:8000/docs**: documentação interativa, onde cada endpoint pode ser testado. Funciona sem internet.

## Endpoints
| Método | Rota            | Descrição                    | Respostas   |
|--------|-----------------|------------------------------|-------------|
| GET    | /pontos         | Lista todos os pontos        | 200         |
| GET    | /pontos/{id}    | Mostra um ponto              | 200 ou 404  |
| POST   | /pontos         | Cadastra um ponto novo       | 201 ou 400  |
| PUT    | /pontos/{id}    | Atualiza um ponto            | 200, 400 ou 404 |
| DELETE | /pontos/{id}    | Apaga um ponto               | 204 ou 404  |

Campos obrigatórios (POST e PUT): `nome`, `cidade`, `descricao`, `latitude` (-90 a 90) e `longitude` (-180 a 180).
Se faltar algum campo ou o valor for inválido, a API responde 400.

## Exemplo de requisição
```
POST /pontos
{"nome": "Parque Zoobotânico", "cidade": "Rio Branco",
 "descricao": "Área verde da UFAC com trilhas e fauna local.",
 "latitude": -9.9556, "longitude": -67.8700}
```
Resposta (201):
```
{"id": 11, "nome": "Parque Zoobotânico", "cidade": "Rio Branco",
 "descricao": "Área verde da UFAC com trilhas e fauna local.",
 "latitude": -9.9556, "longitude": -67.87}
```

## Ferramentas utilizadas
- Claude: geração inicial do código e da página com mapa, que o grupo revisou, testou e modificou onde achou necessário.
- - Leaflet e OpenStreetMap: biblioteca e imagens do mapa (gratuitos, sem chave).
