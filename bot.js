require("dotenv").config();
const bot = require("nodemw");

const client = new bot({
protocol: "https",
server: "test.wikipedia.org",
path: "/w",
debug: false,
username: process.env.WIKI_USER,
password: process.env.WIKI_PASS,
userAgent: process.env.WIKI_AGENT
});

const templateNames = [
    'Template:Info/Filme',
    'Template:Info/Biografia',
    'Template:Info/Empresa',
    'Template:Info/música/artista',
    'Template:Info/Futebolista'
];
const editSummary = 'Substituindo ícones de bandeira por nomes de países ligados na infocaixa';

const countryMap = {
'{{BRA}}': '[[Brasil]]',
'{{EUA}}': '[[Estados Unidos]]',
'{{FRA}}': '[[França]]',
'{{PRT}}': '[[Portugal]]',
};

function replaceFlagsInWikitext(content) {
let newContent = content;

for (const [flag, country] of Object.entries(countryMap)) {
newContent = newContent.replaceAll(flag, country);
}

return newContent;
}

function processPage(pageTitle, retries = 3) {
    client.getArticle(pageTitle, (err, content) => {
        if (err) return console.error(`Erro ao obter ${pageTitle}:`, err);

        const updatedContent = replaceFlagsInWikitext(content);

        if (updatedContent !== content) {
            console.log(`Alterações detectadas em ${pageTitle}. Editando...`);
            client.edit(pageTitle, updatedContent, editSummary, false, (err, res) => {
                if (err) {
                    if (retries > 0 && err.message.includes('503')) {
                        console.log(`503 recebido. Tentando novamente ${pageTitle} (${retries} tentativas restantes)...`);
                        setTimeout(() => processPage(pageTitle, retries - 1), 5000);
                    } else {
                        console.error(`Erro ao editar ${pageTitle}:`, err);
                    }
                    return;
                }
                console.log(`Página ${pageTitle} editada com sucesso!`);
            });
        } else {
            console.log(`Nenhuma alteração em ${pageTitle}.`);
        }
    });
}

client.logIn((err) => {
    if (err) return console.error("Erro ao fazer login:", err);
    console.log("Logado com sucesso!");

    function collectAndProcess() {
        templateNames.forEach(template => {
            client.getPagesTranscluding(template, (err, pages) => {
                if (err) return console.error(`Erro ao buscar páginas de ${template}:`, err);

                console.log(`Encontradas ${pages.length} páginas afluentes do template ${template}.`);

                pages.forEach((page, index) => {
                    if (!page) return;

                    let pageTitle;
                    let ns;

                    if (typeof page === 'string') {
                        pageTitle = page;
                        ns = 0;
                    } else if (page.title) {
                        pageTitle = page.title;
                        ns = page.ns ?? 0;
                    } else {
                        return;
                    }

                    if (ns === 0) {
                        setTimeout(() => processPage(pageTitle), index * 20000);
                    }
                });
            });
        });
    }

    collectAndProcess();
});