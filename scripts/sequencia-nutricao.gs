/**
 * Sequência de nutrição — Desbravando Rust
 *
 * Complementa o autorresponder do capítulo (autorresposta-capitulo-html.gs).
 * Envia e-mails #2, #3 e #4 em D+2, D+5 e D+9 após a captura do lead.
 *
 * Instalação:
 *  1. Abrir a planilha de respostas do Form → Extensões → Apps Script.
 *  2. Colar este arquivo.
 *  3. Ajustar as constantes (SHEET_NAME, colunas, links).
 *  4. Criar gatilho de tempo: enviarSequencia, "Baseado em tempo" → "Dia" (1x/dia).
 *  5. Rodar testeSequenciaDryRun() uma vez para conferir os logs antes de ativar.
 */

const SHEET_NAME = 'Respostas ao formulário 1'; // ajuste ao nome real da aba
const COL_TIMESTAMP = 1;   // A
const COL_EMAIL = 2;       // ajuste: coluna do e-mail
const COL_NOME = 3;        // ajuste: coluna do nome (ou 0 se não houver)
const STAGE_HEADER = 'seq_stage';
const REMETENTE = 'José Luis — Desbravando Rust';
const KIWIFY_URL = 'https://pay.kiwify.com.br/18ZoOt1';
const SITE = 'https://desbravandorust.com.br';

// E-mails da sequência: dias após captura + assunto + corpo (HTML simples inline).
const SEQUENCIA = [
  { dia: 2, assunto: 'O que mais tem dentro do Desbravando Rust',
    html: function (nome) { return corpo(nome,
      'Já deu uma olhada no capítulo? Ele é só a ponta. O livro tem 30 capítulos e 3 projetos completos — API REST com Axum, TOTP com Lambdas e uma CLI de arquivos.',
      'Ver o blog com benchmarks reais', SITE + '/blog/'); } },
  { dia: 5, assunto: 'Por que ownership deixa de assustar',
    html: function (nome) { return corpo(nome,
      'A parte que mais trava quem vem do Python é ownership. O livro dedica capítulos inteiros a ownership, borrowing e lifetimes — com o equivalente em Python lado a lado. Depois disso, o resto flui.',
      'Ler um post sobre ownership', SITE + '/posts/0005-entendendo-ownership-rust-guia-pythonistas/'); } },
  { dia: 9, assunto: 'Sua jornada do Python ao Rust — R$ 89,90',
    html: function (nome) { return corpo(nome,
      'Se o capítulo fez sentido, o livro completo é o caminho mais direto do Python ao Rust: claro, prático e sem recomeçar do zero. Garantia incondicional de 7 dias.',
      'Garantir meu exemplar', KIWIFY_URL); } },
];

function enviarSequencia() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  const data = sheet.getDataRange().getValues();
  const header = data[0];
  let stageCol = header.indexOf(STAGE_HEADER);
  if (stageCol === -1) { stageCol = header.length; sheet.getRange(1, stageCol + 1).setValue(STAGE_HEADER); }

  const agora = new Date();
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const email = row[COL_EMAIL - 1];
    if (!email) continue;
    const capturado = new Date(row[COL_TIMESTAMP - 1]);
    const diasPassados = Math.floor((agora - capturado) / 86400000);
    const stage = Number(row[stageCol] || 0);
    if (stage >= SEQUENCIA.length) continue;

    const proximo = SEQUENCIA[stage];
    if (diasPassados >= proximo.dia) {
      const nome = COL_NOME ? String(row[COL_NOME - 1] || 'Leitor(a)').split(' ')[0] : 'Leitor(a)';
      enviar_(email, proximo.assunto, proximo.html(nome));
      sheet.getRange(i + 1, stageCol + 1).setValue(stage + 1);
    }
  }
}

function enviar_(email, assunto, html) {
  MailApp.sendEmail({ to: email, subject: assunto, htmlBody: html, name: REMETENTE });
}

function corpo(nome, texto, ctaLabel, ctaUrl) {
  return '<div style="font-family:Arial,sans-serif;max-width:600px;color:#1b2740;">' +
    '<p>Olá, ' + nome + '!</p><p>' + texto + '</p>' +
    '<p><a href="' + ctaUrl + '" style="display:inline-block;background:#f74c00;color:#fff;' +
    'padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;">' + ctaLabel + '</a></p>' +
    '<p style="color:#7d8aa0;font-size:13px;">José Luis · Desbravando Rust · ' +
    '<a href="' + SITE + '">desbravandorust.com.br</a></p></div>';
}

/** QA: loga o que seria enviado hoje, sem enviar nada. */
function testeSequenciaDryRun() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  const data = sheet.getDataRange().getValues();
  const header = data[0];
  const stageCol = header.indexOf(STAGE_HEADER);
  const agora = new Date();
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const email = row[COL_EMAIL - 1];
    if (!email) continue;
    const dias = Math.floor((agora - new Date(row[COL_TIMESTAMP - 1])) / 86400000);
    const stage = stageCol === -1 ? 0 : Number(row[stageCol] || 0);
    if (stage < SEQUENCIA.length && dias >= SEQUENCIA[stage].dia) {
      Logger.log('ENVIARIA e-mail #' + (stage + 2) + ' para ' + email + ' (D+' + dias + ')');
    }
  }
}
