import mwparserfromhell
import time
import pywikibot
from pywikibot import pagegenerators

SITE = pywikibot.Site()
# Resumo de edição
EDIT_SUMMARY = 'Substituindo ícones de bandeira por nomes de países ligados na infocaixa'
TEMPLATE_NAMES = [
    'Template:Info/Filme',
    'Template:Info/Biografia',
    'Template:Info/Empresa',
    'Template:Info/música/artista',
    'Template:Info/Futebolista'
]

# Página contendo a lista de bandeiras a substituir
mapping_page = pywikibot.Page(SITE, "User:MrNinja/Teste")
mapping_page.purge()
raw_text = mapping_page.get(force=True)

COUNTRY_MAP = {}
for line in raw_text.splitlines():
    if '=' in line and line.strip():
        flag, country = line.split('=', 1)
        COUNTRY_MAP[flag.strip()] = country.strip()

print("Mapa de bandeiras atualizado:", COUNTRY_MAP)


def replace_flags_in_infobox(content):
    code = mwparserfromhell.parse(content)

    for template in code.filter_templates():
        if template.name.matches('Info/Filme') or \
           template.name.matches('Info/Biografia') or \
           template.name.matches('Info/Empresa') or \
           template.name.matches('Info/música/artista') or \
           template.name.matches('Info/Futebolista'):

            for flag, country in COUNTRY_MAP.items():
                for param in template.params:
                    param.value = str(param.value).replace(flag, country)

    return str(code)


def process_page(page):
    try:
        content = page.get()
    except pywikibot.exceptions.NoPageError:
        print(f"Página {page.title()} não existe. Pulando.")
        return
    except pywikibot.exceptions.IsRedirectPageError:
        print(f"Página {page.title()} é um redirecionamento. Pulando.")
        return
    except pywikibot.exceptions.OtherPageError as err:
        print(f"Erro ao obter {page.title()}: {err}")
        return

    updated_content = replace_flags_in_infobox(content)

    if updated_content != content:
        print(f"Alterações detectadas em {page.title()}. Editando...")
        try:
            page.put(updated_content, summary=EDIT_SUMMARY, minor=True)
            print(f"Página {page.title()} editada com sucesso!")
            time.sleep(20)
        except pywikibot.exceptions.LockedPageError:
            print(f"Página {page.title()} está protegida/bloqueada. Pulando.")
        except pywikibot.exceptions.EditConflictError:
            print(f"Conflito de edição em {page.title()}. Pulando.")
        except pywikibot.exceptions.SpamfilterError as err:
            print(f"Filtro de edições ativado em {page.title()}: {err.args[0]}")
        except pywikibot.exceptions.OtherPageError as err:
            print(f"Erro ao editar {page.title()}: {err.args[0]}")
    else:
        print(f"Nenhuma alteração em {page.title()}.")


def main():
    for template_name in TEMPLATE_NAMES:
        template = pywikibot.Page(SITE, template_name)
        print(f"Buscando páginas afluentes de {template.title()}...")

        referencing_pages = pywikibot.Page(SITE, template_name).backlinks(namespaces=[0])

        pages_list = list(referencing_pages)
        print(f"Encontradas {len(pages_list)} páginas afluentes.")

        for i, page in enumerate(pages_list):
            print(f"\nProcessando página {i+1}/{len(pages_list)}: {page.title()}")
            process_page(page)


if __name__ == "__main__":
    main()
