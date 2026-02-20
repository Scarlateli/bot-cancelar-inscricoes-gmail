# 🤖 Bot de Cancelamento de Inscrições Gmail

Bot automatizado inteligente que cancela inscrições de email usando a aba "Gerenciar inscrições" do Gmail.

## ✨ Funcionalidades

- ✅ Cancela automaticamente todas as inscrições possíveis
- 🧠 Detecta e pula inscrições que redirecionam para sites externos
- 🎯 Fecha automaticamente popup "Acessar o site" do Gmail
- 📊 Mostra estatísticas completas ao final
- 🔄 Não entra em loop - pula inscrições problemáticas
- 💾 Usa perfil Chrome separado (mantém login entre execuções)
- ⚡ Anti-detecção - Gmail não bloqueia

## 📋 Como Funciona

O bot:
1. Acessa a aba "Gerenciar inscrições" do Gmail
2. Encontra todos os botões "Cancelar inscrição" visíveis
3. Para cada inscrição:
   - Clica no botão "Cancelar inscrição"
   - Se aparecer popup "Acessar o site": clica em "Bloquear" e ignora
   - Se redirecionar para site externo: volta e ignora
   - Se cancelar com sucesso: marca como cancelada
4. Continua até processar todas as inscrições
5. Mostra estatísticas finais:
   - Total canceladas
   - Total ignoradas (requerem site externo)

## 🚀 Instalação

### 1. Instalar dependências

Execute no terminal (na pasta raiz do projeto):

```bash
./instalar.sh
```

Isso vai:
- Criar ambiente virtual Python
- Instalar Selenium

### 2. Executar o bot

```bash
./executar.sh
```

## ⚙️ Uso

1. **Execute o script** `./executar.sh`
2. **Aguarde o Chrome abrir** e faça login no Gmail se necessário
3. **O bot vai começar** a cancelar as inscrições automaticamente
4. **Acompanhe o progresso** no terminal
5. **Para parar**, pressione `Ctrl+C` a qualquer momento

## 📊 O que você verá no terminal

```
🤖 Bot de Cancelamento de Inscrições Gmail
==================================================

📋 INSTRUÇÕES:
1. Você precisa estar logado no Gmail
2. O bot vai acessar a aba 'Gerenciar inscrições'
3. Vai clicar em todos os botões 'Cancelar inscrição'
4. Para parar, pressione Ctrl+C a qualquer momento

▶ Pressione ENTER para iniciar...

--- Procurando botões 'Cancelar inscrição' (Canceladas: 0) ---
Encontrados 15 botões de cancelar inscrição

Cancelando: Apple Newsletter
✓ Inscrição cancelada com sucesso!

--- Procurando botões 'Cancelar inscrição' (Canceladas: 1) ---
Cancelando: Marketing Company
⚠ Gmail indica que precisa acessar site externo. Clicando em 'Bloquear'...
✓ Popup fechado. Pulando para próxima inscrição...

--- Procurando botões 'Cancelar inscrição' (Canceladas: 1) ---
...

==================================================
🎉 Automação finalizada!
Total de inscrições canceladas: 12
Inscrições que redirecionam para site externo (ignoradas): 3
==================================================
```

## 🛑 Como Parar

- Pressione `Ctrl+C` no terminal a qualquer momento
- O bot mostrará quantas inscrições foram canceladas até ali

## ⚠️ Observações Importantes

### ✅ O que o bot CANCELA automaticamente:
- Inscrições que têm botão "Cancelar inscrição" direto no Gmail
- Inscrições que mostram popup de confirmação no próprio Gmail

### ❌ O que o bot IGNORA (não consegue cancelar):
- Inscrições que redirecionam para sites externos
- Inscrições que mostram popup "Acesse o site do remetente"
- Essas serão contabilizadas como "ignoradas" no final

### 💡 Dicas:
- O bot usa um **perfil Chrome separado**, então:
  - Não precisa fechar seu Chrome normal
  - O login do Gmail fica salvo entre execuções
  - Na primeira execução, você precisará fazer login
- Se quiser parar, pressione `Ctrl+C` no terminal
- O bot é seguro e não acessa informações pessoais

## 📚 Documentação Completa

Para entender melhor o código e as soluções implementadas:

- **[EXPLICACAO_CODIGO.md](EXPLICACAO_CODIGO.md)** - Explicação linha por linha de todo o código
- **[HISTORICO_PROBLEMAS_E_SOLUCOES.md](HISTORICO_PROBLEMAS_E_SOLUCOES.md)** - Todos os problemas encontrados e como foram resolvidos

## 🔧 Tecnologias Utilizadas

- **Python 3.x**
- **Selenium WebDriver** - Automação do navegador
- **Chrome/Chromium** - Navegador controlado
- **XPath** - Localização de elementos na página

## 🐛 Solução de Problemas

### O bot não encontra o menu "Gerenciar inscrições"
- **Solução**: O bot tenta acessar via URL direta automaticamente
- Verifique se você está logado no Gmail

### O bot está muito rápido/lento
- Ajuste os valores de `time.sleep()` no código
- Linhas principais: 121, 139, 147, 159, 201

### Chrome não abre
- Verifique se o ChromeDriver está instalado
- Execute novamente: `./instalar.sh`

### Erro "selenium not found"
- O ambiente virtual não está ativado
- Execute: `./executar.sh` (ativa automaticamente)

### O bot cancela poucas inscrições
- Normal! Muitas empresas exigem cancelamento via site externo
- O bot mostra quantas foram ignoradas ao final
- **v4.2+**: Bot agora faz scroll automático para encontrar todas as inscrições

### Bot muito lento ou travando ao abrir
- Problema: Perfil do Chrome pode estar corrompido
- Solução: Delete a pasta `chrome_profile` e execute novamente
- Comando: `rm -rf chrome_profile && ./executar.sh`

### Erro ao pressionar Ctrl+C no início
- Corrigido na v4.1
- Se ainda acontecer, atualize o código para a versão mais recente

## 📈 Histórico de Versões

### v4.2 (Atual) ✅
- ✅ Auto-scroll inteligente para carregar mais inscrições
- ✅ Processa TODAS as inscrições (não apenas primeiras visíveis)
- ✅ Tenta scroll até 3x antes de desistir
- ✅ Detecta automaticamente quando não há mais inscrições

### v4.1
- ✅ Otimização de performance: ~50% mais rápido
- ✅ Tempos de espera reduzidos (2s → 1s por inscrição)
- ✅ Correção do bug ao pressionar Ctrl+C durante inicialização
- ✅ Melhor tratamento de erros

### v4.0
- ✅ Detecção e fechamento automático do popup "Acessar o site"
- ✅ Sistema de memória para não reprocessar inscrições
- ✅ Estatísticas completas (canceladas + ignoradas)
- ✅ Documentação completa do código

### v3.0
- ✅ Detecção precisa de redirecionamentos
- ✅ Removida detecção ampla que gerava falsos positivos

### v2.0
- ✅ Sistema de inscrições ignoradas
- ✅ Evita loop infinito

### v1.0
- ✅ Versão básica funcional

## 🤝 Contribuições

Este bot foi desenvolvido para fins educacionais e uso pessoal. Sinta-se livre para modificar e adaptar conforme necessário.

## 📝 Licença

Uso livre para fins pessoais e educacionais.
