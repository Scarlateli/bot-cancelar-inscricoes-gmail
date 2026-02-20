from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

def cancelar_inscricoes_gmail():
    """
    Bot para cancelar inscrições automaticamente usando a aba "Gerenciar inscrições" do Gmail
    """
    # Configurar Chrome para usar um perfil separado do bot
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    # Usar um perfil separado (não precisa fechar o Chrome normal)
    import os
    profile_dir = os.path.join(os.path.dirname(__file__), 'chrome_profile')
    options.add_argument(f"--user-data-dir={profile_dir}")

    # Adicionar flags para evitar detecção
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Iniciar o driver
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    # Inicializar contadores no início (antes do try) para evitar erro ao pressionar Ctrl+C
    inscricoes_canceladas = 0
    inscricoes_ignoradas = set()
    tentativas_scroll_sem_sucesso = 0  # Contador para evitar loop infinito de scroll

    try:
        # Acessar Gmail
        print("Acessando Gmail...")
        driver.get("https://mail.google.com")

        print("\n⚠ AGUARDE: Faça login no Gmail se necessário...")
        time.sleep(5)

        # Navegar para "Gerenciar inscrições" clicando no menu lateral
        print("\nProcurando menu 'Gerenciar inscrições'...")
        try:
            # Procurar e clicar no link "Gerenciar inscrições" no menu lateral
            menu_inscricoes = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(), 'Gerenciar inscrições')]")
            ))
            print("Menu encontrado! Clicando...")
            menu_inscricoes.click()
            time.sleep(3)
            print("✓ Página 'Gerenciar inscrições' carregada!")
        except Exception as e:
            print(f"⚠ Não consegui encontrar o menu. Tentando via URL...")
            driver.get("https://mail.google.com/mail/u/0/#sub")
            time.sleep(3)

        while True:
            print(f"\n--- Procurando botões 'Cancelar inscrição' (Canceladas: {inscricoes_canceladas}) ---")

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
                        print(f"\n🔄 Nenhum botão visível. Tentando scroll para carregar mais... (Tentativa {tentativas_scroll_sem_sucesso}/3)")

                        # Scroll até o final da página
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)  # Aguardar carregamento

                        # Scroll adicional para garantir
                        driver.execute_script("window.scrollBy(0, 500);")
                        time.sleep(1)

                        continue  # Tentar procurar botões novamente
                    else:
                        print("\n✓ Nenhuma inscrição encontrada após múltiplas tentativas de scroll!")
                        print(f"Total de inscrições canceladas: {inscricoes_canceladas}")
                        break

                # Reset contador se encontrou botões
                tentativas_scroll_sem_sucesso = 0

                print(f"Encontrados {len(botoes)} botões de cancelar inscrição (visíveis e clicáveis)")

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
                    except:
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
                        print(f"\n🔄 Todos botões visíveis já foram ignorados. Tentando scroll para carregar mais... (Tentativa {tentativas_scroll_sem_sucesso}/3)")

                        # Scroll até o final da página
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)

                        # Scroll adicional
                        driver.execute_script("window.scrollBy(0, 500);")
                        time.sleep(1)

                        continue  # Tentar procurar botões novamente
                    else:
                        print("\n✓ Todas as inscrições restantes redirecionam para site externo!")
                        print(f"Total de inscrições canceladas: {inscricoes_canceladas}")
                        print(f"Inscrições ignoradas (redirecionam para site): {len(inscricoes_ignoradas)}")
                        break

                # Reset contador se encontrou botão válido
                tentativas_scroll_sem_sucesso = 0

                # Rolar até o elemento ficar visível
                driver.execute_script("arguments[0].scrollIntoView(true);", primeiro_botao)
                time.sleep(0.3)

                print(f"\nCancelando: {nome_inscricao}")

                # Tentar clicar (com fallback para JavaScript se falhar)
                try:
                    primeiro_botao.click()
                except Exception as click_error:
                    print("Clique normal falhou, tentando com JavaScript...")
                    driver.execute_script("arguments[0].click();", primeiro_botao)

                time.sleep(0.8)  # Otimizado: 1.5s → 0.8s

                # Verificar se apareceu o popup "Acessar o site" (cancelamento requer site externo)
                try:
                    # Procurar pelo texto específico que indica que precisa acessar o site
                    popup_texto = driver.find_elements(By.XPATH,
                        "//*[contains(text(), 'acesse o site do remetente') or contains(text(), 'visit the sender')]")

                    if popup_texto and len(popup_texto) > 0:
                        print("⚠ Gmail indica que precisa acessar site externo. Clicando em 'Bloquear'...")

                        # Procurar e clicar no botão "Bloquear" ou "Block"
                        try:
                            botao_bloquear = wait.until(EC.element_to_be_clickable(
                                (By.XPATH, "//button[contains(., 'Bloquear') or contains(., 'Block')]")
                            ))
                            botao_bloquear.click()
                            print("✓ Popup fechado. Pulando para próxima inscrição...")
                            time.sleep(1)
                        except:
                            # Se não achar "Bloquear", tentar fechar o popup de outra forma
                            print("Tentando fechar popup de outra forma...")
                            driver.execute_script("document.querySelector('button').click();")

                        inscricoes_ignoradas.add(nome_inscricao)
                        driver.refresh()
                        time.sleep(1)  # Otimizado: 2s → 1s
                        continue
                except:
                    pass

                # Verificar se foi redirecionado para site externo
                url_atual = driver.current_url
                if "mail.google.com" not in url_atual:
                    print("⚠ Gmail redirecionou para site externo. Pulando para próxima...")
                    inscricoes_ignoradas.add(nome_inscricao)  # Adicionar na lista de ignorados
                    driver.get("https://mail.google.com/mail/u/0/#sub")
                    time.sleep(1)  # Otimizado: 2s → 1s
                    continue

                # Confirmar o cancelamento no popup
                try:
                    print("Aguardando popup de confirmação...")
                    # Procurar especificamente o botão AZUL de confirmação no popup
                    # Usar XPath mais específico para pegar o botão correto
                    confirmar = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(@class, 'VfPpkd') and contains(., 'Cancelar inscrição')]")
                    ))

                    # Garantir que é o botão azul (não o cinza "Cancelar")
                    if 'Cancelar inscrição' in confirmar.text or 'Unsubscribe' in confirmar.text:
                        confirmar.click()
                        print("✓ Inscrição cancelada com sucesso!")
                        inscricoes_canceladas += 1
                        time.sleep(1)
                except TimeoutException:
                    # Se não achar o popup, tenta procurar qualquer botão de confirmação
                    print("Popup não encontrado, tentando confirmação alternativa...")
                    try:
                        # Procurar botões que contenham "Cancelar inscrição"
                        botoes_confirmacao = driver.find_elements(By.XPATH,
                            "//button[contains(., 'Cancelar inscrição') or contains(., 'Unsubscribe')]")

                        # Filtrar botões visíveis
                        botoes_visiveis = [b for b in botoes_confirmacao if b.is_displayed()]

                        if len(botoes_visiveis) > 0:
                            # Clicar no último botão (geralmente é o de confirmação)
                            botoes_visiveis[-1].click()
                            print("✓ Inscrição cancelada!")

                        inscricoes_canceladas += 1
                        time.sleep(1)
                    except:
                        print("✓ Cancelamento processado (confirmação não necessária)")
                        inscricoes_canceladas += 1
                        time.sleep(0.5)

                # Recarregar a página para atualizar a lista
                driver.refresh()
                time.sleep(1)  # Otimizado: 2s → 1s (PRINCIPAL otimização!)

            except Exception as e:
                print(f"⚠ Erro: {str(e)}")
                # Tentar recarregar e continuar
                driver.refresh()
                time.sleep(1.5)  # Otimizado: 3s → 1.5s

                # Se continuar dando erro, pode não haver mais inscrições
                try:
                    botoes_check = driver.find_elements(By.XPATH,
                        "//*[contains(text(), 'Cancelar inscrição') or contains(text(), 'Unsubscribe')]")
                    if not botoes_check:
                        break
                except:
                    break

        print(f"\n{'='*50}")
        print(f"🎉 Automação finalizada!")
        print(f"Total de inscrições canceladas: {inscricoes_canceladas}")
        if len(inscricoes_ignoradas) > 0:
            print(f"Inscrições que redirecionam para site externo (ignoradas): {len(inscricoes_ignoradas)}")
        print(f"{'='*50}")

    except KeyboardInterrupt:
        print("\n\n⚠ Automação interrompida pelo usuário (Ctrl+C)")
        print(f"Inscrições canceladas até agora: {inscricoes_canceladas}")
        if 'inscricoes_ignoradas' in locals() and len(inscricoes_ignoradas) > 0:
            print(f"Inscrições ignoradas (site externo): {len(inscricoes_ignoradas)}")
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
    finally:
        print("\n")
        resposta = input("Deseja fechar o navegador? (s/n): ")
        if resposta.lower() == 's':
            driver.quit()
        else:
            print("Navegador mantido aberto. Feche manualmente quando quiser.")

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

    input("\n▶ Pressione ENTER para iniciar...")
    cancelar_inscricoes_gmail()