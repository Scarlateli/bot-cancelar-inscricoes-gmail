from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import sys
import logging

# Configurar logging (console + arquivo)
log_dir = os.path.dirname(__file__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, 'bot.log'), encoding='utf-8'),
    ]
)
log = logging.getLogger(__name__)

def cancelar_inscricoes_gmail():
    """
    Bot para cancelar inscrições automaticamente usando a aba "Gerenciar inscrições" do Gmail
    """
    # Configurar Chrome para usar um perfil separado do bot
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    # Usar um perfil separado (não precisa fechar o Chrome normal)
    profile_dir = os.path.join(os.path.dirname(__file__), 'chrome_profile')
    options.add_argument(f"--user-data-dir={profile_dir}")

    # Adicionar flags para evitar detecção
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Iniciar o driver
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        log.error(f"Não foi possível abrir o Chrome. Verifique se o ChromeDriver está instalado.")
        log.error(f"Detalhes: {e}")
        return

    wait = WebDriverWait(driver, 10)

    # Inicializar contadores no início (antes do try) para evitar erro ao pressionar Ctrl+C
    inscricoes_canceladas = 0
    inscricoes_ignoradas = set()
    tentativas_scroll_sem_sucesso = 0  # Contador para evitar loop infinito de scroll

    try:
        # Acessar Gmail (timeout maior só para o carregamento inicial)
        log.info("Acessando Gmail...")
        driver.set_page_load_timeout(30)
        try:
            driver.get("https://mail.google.com")
        except Exception:
            log.info("Timeout no carregamento inicial, tentando parar e continuar...")
            driver.execute_script("window.stop()")
        # Restaurar timeout rápido para as demais operações
        driver.set_page_load_timeout(10)

        log.info("AGUARDE: Faça login no Gmail se necessário...")
        time.sleep(5)

        # Navegar para "Gerenciar inscrições" clicando no menu lateral
        log.info("Procurando menu 'Gerenciar inscrições'...")
        try:
            botao_mais = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(), 'Mais')]")
            ))
            botao_mais.click()
            time.sleep(1)
            menu_inscricoes = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(), 'Gerenciar inscrições')]")
            ))
            log.info("Menu encontrado! Clicando...")
            menu_inscricoes.click()
            time.sleep(3)
            log.info("Página 'Gerenciar inscrições' carregada!")
        except Exception:
            log.info("Não consegui encontrar o menu. Tentando via URL...")
            driver.get("https://mail.google.com/mail/u/0/#sub")
            time.sleep(3)

        while True:
            log.info(f"--- Procurando botões 'Cancelar inscrição' (Canceladas: {inscricoes_canceladas}) ---")

            try:
                # Procurar todos os elementos "Cancelar inscrição" na página
                # Filtra apenas os VISÍVEIS e CLICÁVEIS
                todos_elementos = driver.find_elements(By.XPATH,
                    "//*[contains(text(), 'Cancelar inscrição') or contains(text(), 'Unsubscribe')]")

                # Filtrar apenas elementos visíveis e clicáveis
                botoes = [btn for btn in todos_elementos if btn.is_displayed() and btn.is_enabled()]

                if not botoes or len(botoes) == 0:
                    # Antes de desistir, tentar scroll para carregar mais inscrições
                    if tentativas_scroll_sem_sucesso < 3:
                        tentativas_scroll_sem_sucesso += 1
                        log.info(f"Nenhum botão visível. Tentando scroll para carregar mais... (Tentativa {tentativas_scroll_sem_sucesso}/3)")

                        # Scroll até o final da página
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)  # Aguardar carregamento

                        # Scroll adicional para garantir
                        driver.execute_script("window.scrollBy(0, 500);")
                        time.sleep(1)

                        continue  # Tentar procurar botões novamente
                    else:
                        log.info("Nenhuma inscrição encontrada após múltiplas tentativas de scroll!")
                        log.info(f"Total de inscrições canceladas: {inscricoes_canceladas}")
                        break

                # Reset contador se encontrou botões
                tentativas_scroll_sem_sucesso = 0

                log.info(f"Encontrados {len(botoes)} botões de cancelar inscrição")

                # Procurar o primeiro botão que NÃO está na lista de ignorados
                primeiro_botao = None
                nome_inscricao = "inscrição"

                for botao in botoes:
                    # Tentar pegar o nome da empresa/serviço
                    try:
                        elemento_pai = botao.find_element(By.XPATH, "./ancestor::tr")
                        nome_temp = elemento_pai.text.split('\n')[0]

                        # Se não estiver na lista de ignorados, usar este botão
                        if nome_temp not in inscricoes_ignoradas:
                            primeiro_botao = botao
                            nome_inscricao = nome_temp
                            break
                    except Exception:
                        # Se não conseguir pegar o nome, tentar pelo índice
                        indice = botoes.index(botao)
                        nome_temp = f"inscricao_indice_{indice}"

                        if nome_temp not in inscricoes_ignoradas:
                            primeiro_botao = botao
                            nome_inscricao = nome_temp
                            break

                # Se todos os botões estão ignorados, tentar scroll antes de desistir
                if primeiro_botao is None:
                    if tentativas_scroll_sem_sucesso < 3:
                        tentativas_scroll_sem_sucesso += 1
                        log.info(f"Todos botões visíveis já ignorados. Tentando scroll... (Tentativa {tentativas_scroll_sem_sucesso}/3)")

                        # Scroll até o final da página
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)

                        # Scroll adicional
                        driver.execute_script("window.scrollBy(0, 500);")
                        time.sleep(1)

                        continue  # Tentar procurar botões novamente
                    else:
                        log.info("Todas as inscrições restantes redirecionam para site externo!")
                        log.info(f"Total canceladas: {inscricoes_canceladas}")
                        log.info(f"Ignoradas (site externo): {len(inscricoes_ignoradas)}")
                        break

                # Reset contador se encontrou botão válido
                tentativas_scroll_sem_sucesso = 0

                # Rolar até o elemento ficar visível
                driver.execute_script("arguments[0].scrollIntoView(true);", primeiro_botao)
                time.sleep(0.3)

                log.info(f"Cancelando: {nome_inscricao}")

                # Tentar clicar (com fallback para JavaScript se falhar)
                try:
                    primeiro_botao.click()
                except Exception:
                    log.info("Clique normal falhou, tentando com JavaScript...")
                    driver.execute_script("arguments[0].click();", primeiro_botao)

                time.sleep(0.8)  # Otimizado: 1.5s → 0.8s

                # Verificar se apareceu o popup "Acessar o site" (cancelamento requer site externo)
                try:
                    # Procurar pelo texto específico que indica que precisa acessar o site
                    popup_texto = driver.find_elements(By.XPATH,
                        "//*[contains(text(), 'acesse o site do remetente') or contains(text(), 'visit the sender')]")

                    if popup_texto and len(popup_texto) > 0:
                        log.info("Gmail indica que precisa acessar site externo. Clicando em 'Bloquear'...")

                        # Procurar e clicar no botão "Bloquear" ou "Block"
                        try:
                            botao_bloquear = wait.until(EC.element_to_be_clickable(
                                (By.XPATH, "//button[contains(., 'Bloquear') or contains(., 'Block')]")
                            ))
                            botao_bloquear.click()
                            log.info("Popup fechado. Pulando para próxima inscrição...")
                            time.sleep(1)
                        except Exception:
                            # Se não achar "Bloquear", recarregar para fechar o popup
                            log.info("Botão 'Bloquear' não encontrado. Recarregando página...")

                        inscricoes_ignoradas.add(nome_inscricao)
                        driver.refresh()
                        time.sleep(1)
                        continue
                except Exception:
                    pass

                # Verificar se foi redirecionado para site externo
                url_atual = driver.current_url
                if "mail.google.com" not in url_atual:
                    log.info("Gmail redirecionou para site externo. Pulando para próxima...")
                    inscricoes_ignoradas.add(nome_inscricao)
                    driver.get("https://mail.google.com/mail/u/0/#sub")
                    time.sleep(1)
                    continue

                # Confirmar o cancelamento no popup
                try:
                    log.info("Aguardando popup de confirmação...")
                    confirmar = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'VfPpkd') and contains(., 'Cancelar inscrição')]")
                    ))

                    if 'Cancelar inscrição' in confirmar.text or 'Unsubscribe' in confirmar.text:
                        confirmar.click()
                        log.info("Inscrição cancelada com sucesso!")
                        inscricoes_canceladas += 1
                        time.sleep(1)
                except TimeoutException:
                    # Se não achar o popup, tenta procurar qualquer botão de confirmação
                    log.info("Popup não encontrado, tentando confirmação alternativa...")
                    try:
                        botoes_confirmacao = driver.find_elements(By.XPATH,
                            "//button[contains(., 'Cancelar inscrição') or contains(., 'Unsubscribe')]")

                        botoes_visiveis = [b for b in botoes_confirmacao if b.is_displayed()]

                        if len(botoes_visiveis) > 0:
                            botoes_visiveis[-1].click()
                            log.info("Inscrição cancelada!")
                            inscricoes_canceladas += 1
                        else:
                            log.info("Nenhum botão de confirmação encontrado. Pulando...")
                        time.sleep(1)
                    except Exception:
                        log.info("Cancelamento não confirmado. Pulando...")

                # Recarregar a página para atualizar a lista
                log.info("Recarregando página...")
                try:
                    driver.get("https://mail.google.com/mail/u/0/#sub")
                except Exception:
                    log.info("Timeout no carregamento, tentando parar e continuar...")
                    driver.execute_script("window.stop();")
                time.sleep(2)

            except Exception as e:
                log.error(f"Erro: {str(e)}")
                driver.refresh()
                time.sleep(1.5)

                # Se continuar dando erro, pode não haver mais inscrições
                try:
                    botoes_check = driver.find_elements(By.XPATH,
                        "//*[contains(text(), 'Cancelar inscrição') or contains(text(), 'Unsubscribe')]")
                    if not botoes_check:
                        break
                except Exception:
                    break

        log.info(f"{'='*50}")
        log.info("Automação finalizada!")
        log.info(f"Total de inscrições canceladas: {inscricoes_canceladas}")
        if len(inscricoes_ignoradas) > 0:
            log.info(f"Inscrições que redirecionam para site externo (ignoradas): {len(inscricoes_ignoradas)}")
        log.info(f"{'='*50}")

    except KeyboardInterrupt:
        log.info("\nAutomação interrompida pelo usuário (Ctrl+C)")
        log.info(f"Inscrições canceladas até agora: {inscricoes_canceladas}")
        if len(inscricoes_ignoradas) > 0:
            log.info(f"Inscrições ignoradas (site externo): {len(inscricoes_ignoradas)}")
    except Exception as e:
        log.error(f"Erro fatal: {str(e)}")
    finally:
        print("")
        if sys.stdin.isatty():
            resposta = input("Deseja fechar o navegador? (s/n): ")
            if resposta.lower() == 's':
                driver.quit()
            else:
                print("Navegador mantido aberto. Feche manualmente quando quiser.")
        else:
            print("Fechando navegador automaticamente...")
            driver.quit()

if __name__ == "__main__":
    print("="*50)
    print("🤖 Bot de Cancelamento de Inscrições Gmail")
    print("="*50)
    print("\n📋 INSTRUÇÕES:")
    print("1. Você precisa estar logado no Gmail")
    print("2. O bot vai acessar a aba 'Gerenciar inscrições'")
    print("3. Vai clicar em todos os botões 'Cancelar inscrição'")
    print("4. Para parar, pressione Ctrl+C a qualquer momento")
    print("\n" + "="*50)

    if sys.stdin.isatty():
        sys.stdout.flush()
        time.sleep(0.5)  # Aguarda o terminal do VSCode estabilizar
        sigint_count = 0
        while True:
            try:
                input("\n▶ Pressione ENTER para iniciar...")
                break
            except KeyboardInterrupt:
                sigint_count += 1
                if sigint_count >= 2:
                    print("\nSaindo...")
                    sys.exit(0)
                # Primeiro SIGINT pode ser espúrio (bug do terminal VSCode)
    else:
        print("\n⚠️  AVISO: Execute pelo terminal para usar o modo interativo.")
        print("   Use: ./executar.sh  ou  python3 bot_email.py")
        print("   Iniciando em 3 segundos...")
        time.sleep(3)
    cancelar_inscricoes_gmail()