# Achados e Perdidos da UTFPR

Sistema web para registrar itens perdidos e encontrados no campus da UTFPR. Usuários cadastram itens com foto, comentam, reivindicam itens encontrados e um administrador aprova ou recusa as devoluções, com histórico de status.

Desenvolvido com **Django**, **SQLite** e templates HTML (sem SPA).

## Funcionalidades

- Cadastro, login e logout (e-mail e senha), com perfis Usuário e Admin
- Home pública com lista dos itens mais recentes, filtros por categoria e status e paginação
- Novo Registro (Perdido ou Encontrado) com foto obrigatória e geolocalização opcional
- Detalhes do item, edição e exclusão (somente o autor)
- Alteração de status pelo Admin, com histórico de cada mudança
- Comentários (dialog) e moderação pelo Admin
- Reivindicação de itens encontrados, com aprovação ou recusa pelo Admin
- API JSON somente leitura

## Requisitos

- Python 3.12 ou superior (desenvolvido e testado com Python 3.14)
- Git
- Não é necessário Docker nem banco de dados externo (usa SQLite)

## Instalação e execução

Os comandos abaixo usam Git Bash ou Linux/Mac. No Windows (PowerShell/CMD), as diferenças estão indicadas.

1. Clone o repositório e entre na pasta:

```bash
git clone https://github.com/JoseMarra2006/lost-n-founds_UTFPR.git
cd lost-n-founds_UTFPR
```

2. Crie e ative o ambiente virtual:

```bash
python -m venv venv
source venv/Scripts/activate
```

Linux/Mac: `source venv/bin/activate`. Windows PowerShell: `venv\Scripts\Activate.ps1`. Windows CMD: `venv\Scripts\activate.bat`.

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Crie o arquivo de configuração:

```bash
cp .env.example .env
```

No Windows CMD: `copy .env.example .env`. O valor padrão já funciona para teste local. Para gerar uma chave própria (opcional):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Cole o resultado em `SECRET_KEY` dentro do `.env`.

5. Crie o banco de dados (migrações):

```bash
python manage.py migrate
```

6. Carregue os dados de exemplo (seeds):

```bash
python manage.py seed
```

7. Inicie o servidor:

```bash
python manage.py runserver
```

8. Acesse http://127.0.0.1:8000

Para recomeçar do zero, apague o arquivo `db.sqlite3` e a pasta `media/` e repita os passos 5 e 6.

## Dados de teste

| Perfil | E-mail | Senha |
|---|---|---|
| Admin | admin@utfpr.br | SenhaTeste123! |
| Usuário | usuario@utfpr.br | SenhaTeste123! |

O seed cria 2 usuários e 8 itens em status variados (Perdido, Encontrado, Em verificação, Devolvido e Arquivado), com comentários, uma reivindicação pendente e o histórico de status. As fotos do seed são imagens de cor sólida geradas automaticamente. Rodar o seed mais de uma vez não duplica os dados.

Os logins também funcionam no painel `/admin/` do Django.

## Passo a passo de teste

**Criar um item Perdido ou Encontrado**
1. Entre como `usuario@utfpr.br`.
2. Clique em **Novo Registro** na Home.
3. Escolha o tipo, preencha título, descrição, categoria e local (o botão "Usar minha localização" é opcional) e envie uma foto JPG ou PNG de até 5 MB.
4. Clique em **Cadastrar**. Item Encontrado começa como "Em verificação"; item Perdido começa como "Perdido".

**Comentar**
1. Abra qualquer item clicando no título.
2. Clique no botão flutuante **Adicionar Comentário**, escreva o texto e clique em **Salvar**.

**Reivindicar**
1. Entre como `usuario@utfpr.br` e abra um item **Encontrado** que não esteja devolvido (por exemplo, "Pendrive Kingston 32GB" ou "Garrafa térmica preta").
2. Clique em **Reivindicar**, escreva a prova (imagem opcional) e clique em **Enviar**.

**Aprovar ou recusar**
1. Entre como `admin@utfpr.br`.
2. Clique em **Reivindicações** no topo.
3. **Aprovar** muda o status do item para Devolvido. **Recusar** mantém o status. Ambas as decisões ficam registradas no histórico, na página do item.

**Alterar status e moderar comentários (Admin)**
- Na página de um item, o Admin vê o bloco "Alterar status" e o botão para excluir cada comentário.

## API

Somente leitura (GET). As respostas são JSON, com os itens mais recentes primeiro.

| Rota | Descrição |
|---|---|
| `GET /api/items?status=&category=&page=` | Lista paginada (10 por página) |
| `GET /api/items/{id}` | Detalhes do item, incluindo comentários |

Valores de `status`: `perdido`, `encontrado`, `verificacao`, `devolvido`, `arquivado`.
Valores de `category`: `eletronicos`, `documentos`, `vestuario`, `outros`.

Exemplos:

```bash
curl "http://127.0.0.1:8000/api/items"
curl "http://127.0.0.1:8000/api/items?status=verificacao&category=eletronicos&page=1"
curl "http://127.0.0.1:8000/api/items/1"
```

Exemplo de resposta de `GET /api/items`:

```json
{
  "total": 8,
  "pagina": 1,
  "total_paginas": 1,
  "resultados": [
    {
      "id": 8,
      "titulo": "Chaveiro com três chaves",
      "descricao": "Chaveiro com um pingente de ursinho.",
      "tipo": "encontrado",
      "categoria": "outros",
      "status": "encontrado",
      "local": "Ginásio",
      "foto": "http://127.0.0.1:8000/media/itens/Chaveiro_com_tr.png",
      "autor": "Administrador",
      "criado_em": "2026-10-07T16:55:49.123456+00:00"
    }
  ]
}
```

`GET /api/items/{id}` devolve os mesmos campos mais a lista `comentarios` (`id`, `autor`, `texto`, `criado_em`). Item inexistente devolve `{"erro": "Item não encontrado."}` com status 404. Métodos diferentes de GET devolvem 405. As datas são retornadas em UTC.

## Configuração (.env)

Copie `.env.example` para `.env`:

| Variável | Descrição | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave secreta do Django | valor de desenvolvimento |
| `DEBUG` | `True` em desenvolvimento, `False` em produção | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por vírgula | `127.0.0.1,localhost` |
| `HTTPS` | `True` apenas se o site for servido por HTTPS (cookies seguros) | `False` |
| `USE_S3` | `True` para guardar as fotos em storage S3-compatível | `False` |
| `AWS_*` | Credenciais do storage S3 (só com `USE_S3=True`) | vazio |

O arquivo `.env` não é versionado (está no `.gitignore`).

## Como alternar o storage das fotos

**Local (padrão):** com `USE_S3=False`, as fotos ficam na pasta `media/`, servida pelo Django em desenvolvimento.

**Online (S3-compatível, por exemplo Supabase Storage):**
1. Instale as bibliotecas extras: `pip install -r requirements-s3.txt`
2. Crie um bucket público no provedor e gere as chaves de acesso S3.
3. No `.env`, defina `USE_S3=True` e preencha `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_ENDPOINT_URL` e, se necessário, `AWS_S3_REGION_NAME` e `AWS_S3_CUSTOM_DOMAIN` (endereço público das imagens).
4. Reinicie o servidor. O código das telas não muda: apenas o destino dos arquivos.

## Decisões de arquitetura

- **Django com templates**: o frontend é servido pelo próprio Django, sem SPA separada, por isso não há necessidade de CORS e o CSRF funciona com formulários comuns.
- **Views em função e um app por assunto**: `contas` (cadastro e login) e `itens` (itens, comentários, reivindicações, histórico e API).
- **Perfil Admin** é o campo `is_staff` do usuário do Django.
- **Login pelo e-mail**: o e-mail é gravado como `username`.
- **Validação no backend**: formulários do Django validam campos obrigatórios, tipo e categoria, tipo da imagem (JPG/PNG) e tamanho (5 MB). Status inicial, autor e data são definidos pelo servidor, nunca pelo formulário.
- **Datas em UTC**: o banco guarda em UTC (`USE_TZ = True`) e a interface converte para o horário de Brasília.
- **Segurança**: senhas com hash PBKDF2, CSRF em todos os formulários POST, escape automático de HTML nos templates (anti-XSS), permissões checadas nas views (erro 403), cookies HttpOnly e SameSite, páginas de erro amigáveis e logs de erro no terminal do servidor.
- **Histórico de status**: a tabela `HistoricoStatus` registra cada mudança (cadastro, alteração pelo Admin, aprovação e recusa de reivindicação).
- **Status "Arquivado"**: usado pelo Admin, além dos quatro status exigidos nos filtros.
- **Moderar comentários**: o Admin pode excluir comentários.
- **Regras de reivindicação**: só itens do tipo Encontrado, ainda não devolvidos nem arquivados, e cada usuário só pode ter uma reivindicação pendente por item.

## Limitações e trade-offs

- O modo S3 está implementado e documentado, mas não foi testado com um provedor real.
- O projeto foi preparado para execução local; não há configuração de deploy (servidor de produção, arquivos estáticos otimizados).
- A geolocalização grava latitude e longitude como texto no campo de local, que pode ser editado.
- Fotos do seed são imagens de cor sólida; fotos reais aparecem nos itens cadastrados pelo site.
- A API é somente leitura e sem autenticação, como pede o enunciado.
- Não há envio de e-mails nem notificações.

## Estrutura

```
config/      configurações e URLs principais
contas/      cadastro, login e logout
itens/       models, forms, views, api, urls e comando seed
templates/   páginas HTML
static/      CSS
```