# Bot de Cancelamento de Inscrições Gmail

Bot que automatiza o cancelamento de inscrições de email pelo Gmail, usando a aba "Gerenciar inscrições". Ele percorre os botões de cancelar, lida com popups e redirecionamentos, e mostra um resumo no final.

## Como funciona

1. Abre o Chrome e acessa a aba "Gerenciar inscrições" do Gmail
2. Percorre todos os botões "Cancelar inscrição"
3. Se o cancelamento for direto no Gmail, cancela automaticamente
4. Se redirecionar para site externo ou pedir pra acessar o site do remetente, pula e contabiliza como ignorada
5. Faz scroll automático para carregar todas as inscrições
6. No final, mostra quantas foram canceladas e quantas foram ignoradas

## Instalação

```bash
./instalar.sh
```

Isso cria o ambiente virtual e instala o Selenium.

## Uso

```bash
./executar.sh
```

Na primeira vez, o Chrome vai abrir e você precisa fazer login no Gmail. Depois disso, o login fica salvo (o bot usa um perfil Chrome separado).

Pra parar a qualquer momento: `Ctrl+C`.

## Limitações

- Inscrições que exigem cancelamento via site externo não são canceladas (o bot pula essas)
- Depende da estrutura atual da interface do Gmail — se o Google mudar o layout, pode quebrar

## Problemas comuns

**Chrome não abre** — Verifique se o ChromeDriver está instalado. Rode `./instalar.sh` novamente.

**"selenium not found"** — Use `./executar.sh` que já ativa o ambiente virtual.

**Bot travando ao abrir** — O perfil do Chrome pode estar corrompido. Delete a pasta `chrome_profile` e rode novamente.

**Poucas inscrições canceladas** — Normal. Muitas empresas exigem cancelamento pelo próprio site.

## Tecnologias

- Python 3
- Selenium WebDriver
- Chrome/Chromium

