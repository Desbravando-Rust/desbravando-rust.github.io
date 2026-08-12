/**
 * Newsletter do último post — Desbravando Rust
 *
 * Lê o feed Atom do site, pega o post mais recente e envia um e-mail estilizado
 * (título, resumo, thumb da capa e link) para a lista de assinantes. Gratuito:
 * só usa APIs nativas do Apps Script. Complementa autorresposta-capitulo-html.gs.
 *
 * Instalação:
 *  1. Planilha com uma aba "assinantes": coluna A = e-mails, coluna B = nomes
 *     (a partir da linha 2). O nome pode ficar vazio → cai em "Leitor(a)".
 *  2. Extensões → Apps Script → colar este arquivo.
 *  3. Ajustar PLANILHA_ID (ID da planilha na URL) e conferir FEED_URL.
 *  4. Rodar testeNewsletterDryRun() e conferir os logs (não envia nada).
 *  5. Rodar enviarUltimoPost() manualmente 1x: autoriza escopos, envia o post
 *     atual e grava ultimo_post_id (evita reenvio retroativo).
 *  6. Criar gatilho de tempo: enviarUltimoPost, "Baseado em tempo" → "Dia".
 */

const FEED_URL = 'https://desbravandorust.com.br/feed.xml';
const SITE = 'https://desbravandorust.com.br';
const OG_DEFAULT = SITE + '/imgs/og-default.png';
const PLANILHA_ID = 'COLE_AQUI_O_ID_DA_PLANILHA';
const ABA_ASSINANTES = 'assinantes';
const REMETENTE = 'José Luis — Desbravando Rust';
const ATOM_NS = XmlService.getNamespace('http://www.w3.org/2005/Atom');

function enviarUltimoPost() {
  const entry = primeiraEntry_();
  if (!entry) return;

  const props = PropertiesService.getScriptProperties();
  if (entry.id === props.getProperty('ultimo_post_id')) return; // nada novo

  const assinantes = listaAssinantes_();
  if (!assinantes.length) return;

  const cover = resolverCapa_(entry.link);
  const assunto = 'Novo no Desbravando Rust: ' + entry.titulo;

  // Um e-mail por assinante para personalizar a saudação (Bcc não permite isso).
  // ~10 destinatários ≪ quota de 100/dia.
  assinantes.forEach(function (a) {
    const nome = a.nome || 'Leitor(a)';
    MailApp.sendEmail({
      to: a.email,
      subject: assunto,
      body: 'Olá, ' + nome + '!\n\n' + entry.titulo + '\n\n' + entry.resumo +
        '\n\nLeia na íntegra: ' + entry.link + '\n\n— José Luis · ' + SITE,
      htmlBody: montarHtml_(nome, entry.titulo, entry.resumo, cover, entry.link),
      name: REMETENTE,
    });
  });

  props.setProperty('ultimo_post_id', entry.id);
}

/** Baixa e parseia o feed Atom; retorna a 1ª entry (post mais recente). */
function primeiraEntry_() {
  const xml = UrlFetchApp.fetch(FEED_URL).getContentText();
  const root = XmlService.parse(xml).getRootElement();
  const entry = root.getChild('entry', ATOM_NS);
  if (!entry) return null;
  return {
    titulo: entry.getChildText('title', ATOM_NS),
    resumo: entry.getChildText('summary', ATOM_NS),
    id: entry.getChildText('id', ATOM_NS),
    link: entry.getChild('link', ATOM_NS).getAttribute('href').getValue(),
  };
}

/** Assinantes da aba (col A = e-mail, col B = nome; a partir da linha 2). */
function listaAssinantes_() {
  const aba = SpreadsheetApp.openById(PLANILHA_ID).getSheetByName(ABA_ASSINANTES);
  const ultima = aba.getLastRow();
  if (ultima < 2) return [];
  return aba.getRange(2, 1, ultima - 1, 2).getValues()
    .map(function (r) {
      return { email: String(r[0]).trim(), nome: String(r[1] || '').trim().split(' ')[0] };
    })
    .filter(function (a) { return a.email.indexOf('@') > -1; });
}

/** Capa segue convenção do repo: <postUrl>/imgs/cover.png (fallback jpg → og-default). */
function resolverCapa_(postUrl) {
  const base = postUrl.replace(/\/$/, '');
  const png = base + '/imgs/cover.png';
  const jpg = base + '/imgs/cover.jpg';
  if (existe_(png)) return png;
  if (existe_(jpg)) return jpg;
  return OG_DEFAULT;
}

function existe_(url) {
  try {
    return UrlFetchApp.fetch(url, { muteHttpExceptions: true, followRedirects: false })
      .getResponseCode() === 200;
  } catch (e) { return false; }
}

/**
 * Template na identidade do projeto (dark + laranja #f74c00), tabelas + inline
 * styles para compatibilidade com Gmail/Outlook/Apple Mail.
 */
function montarHtml_(nome, titulo, resumo, coverUrl, postUrl) {
  return '' +
  '<body style=\'margin:0;padding:0;background-color:#0e1524;\'>' +
    '<table role=\'presentation\' width=\'100%\' cellpadding=\'0\' cellspacing=\'0\' style=\'background-color:#0e1524;\'>' +
      '<tr><td align=\'center\' style=\'padding:32px 16px;\'>' +
        '<table role=\'presentation\' width=\'600\' cellpadding=\'0\' cellspacing=\'0\' style=\'width:600px;max-width:600px;background-color:#1b2740;border-radius:16px;border-top:4px solid #f74c00;overflow:hidden;\'>' +

          // Marca
          '<tr><td style=\'padding:32px 40px 16px 40px;font-family:Arial,Helvetica,sans-serif;\'>' +
            '<span style=\'font-size:18px;font-weight:bold;color:#e8edf5;\'>Desbravando <span style=\'color:#ff7a3d;\'>Rust</span></span>' +
          '</td></tr>' +

          // Saudação
          '<tr><td style=\'padding:0 40px 20px 40px;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.6;color:#b8c2d0;\'>' +
            'Olá, ' + nome + '! Saiu post novo no blog 🦀' +
          '</td></tr>' +

          // Capa (clicável)
          '<tr><td style=\'padding:0 40px;\'>' +
            '<a href=\'' + postUrl + '\'>' +
              '<img src=\'' + coverUrl + '\' width=\'520\' alt=\'' + titulo + '\' ' +
              'style=\'display:block;width:100%;max-width:520px;height:auto;border-radius:12px;border:0;\'>' +
            '</a>' +
          '</td></tr>' +

          // Título
          '<tr><td style=\'padding:24px 40px 0 40px;font-family:Arial,Helvetica,sans-serif;\'>' +
            '<h1 style=\'margin:0;font-size:24px;line-height:1.3;color:#e8edf5;\'>' + titulo + '</h1>' +
          '</td></tr>' +

          // Resumo
          '<tr><td style=\'padding:16px 40px 0 40px;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.6;color:#b8c2d0;\'>' +
            '<p style=\'margin:0;\'>' + resumo + '</p>' +
          '</td></tr>' +

          // Botão
          '<tr><td align=\'center\' style=\'padding:28px 40px 8px 40px;\'>' +
            '<table role=\'presentation\' cellpadding=\'0\' cellspacing=\'0\'><tr>' +
              '<td align=\'center\' bgcolor=\'#f74c00\' style=\'border-radius:8px;\'>' +
                '<a href=\'' + postUrl + '\' style=\'display:inline-block;padding:14px 32px;font-family:Arial,Helvetica,sans-serif;font-size:16px;font-weight:bold;color:#ffffff;text-decoration:none;border-radius:8px;\'>Ler na íntegra</a>' +
              '</td>' +
            '</tr></table>' +
          '</td></tr>' +

          // Rodapé + descadastro
          '<tr><td style=\'padding:24px 40px 32px 40px;border-top:1px solid #2a3850;font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.6;color:#7d8aa0;\'>' +
            'José Luis da Cruz Junior · Desbravando Rust<br>' +
            '<a href=\'' + SITE + '\' style=\'color:#ff7a3d;text-decoration:none;\'>desbravandorust.com.br</a><br><br>' +
            'Não quer mais receber? Responda este e-mail com <strong>SAIR</strong>.' +
          '</td></tr>' +

        '</table>' +
      '</td></tr>' +
    '</table>' +
  '</body>';
}

/** QA: loga o último post (título/resumo/capa/link) SEM enviar e SEM gravar property. */
function testeNewsletterDryRun() {
  const entry = primeiraEntry_();
  if (!entry) { Logger.log('Nenhuma entry no feed.'); return; }
  const salvo = PropertiesService.getScriptProperties().getProperty('ultimo_post_id');
  Logger.log('Título : ' + entry.titulo);
  Logger.log('Link   : ' + entry.link);
  Logger.log('Capa   : ' + resolverCapa_(entry.link));
  Logger.log('Resumo : ' + entry.resumo);
  Logger.log('Assinantes: ' + listaAssinantes_().length);
  Logger.log(entry.id === salvo ? 'NÃO enviaria (post já enviado).' : 'ENVIARIA (post novo).');
}
