/**
 * Autorresposta do capítulo grátis — Desbravando Rust (com template HTML)
 *
 * Onde usar: formulário → Editor de script. Cole, ajuste LINK_CAPITULO e mantenha
 * o acionador "Ao enviar o formulário" que você já criou.
 *
 * Regras de e-mail HTML respeitadas: layout em tabelas + estilos inline.
 * O corpo HTML fica numa string com aspas simples, então as aspas dos atributos
 * HTML estão escapadas (\'). É só colar e ajustar o link.
 */

const LINK_CAPITULO = 'COLE_AQUI_O_LINK_DO_DRIVE'; // link do PDF no Google Drive
const ASSUNTO = 'Seu capítulo de Desbravando Rust chegou!';

function enviarCapitulo(e) {
  const resposta = e.response;

  let email = resposta.getRespondentEmail();
  let nome = 'Leitor(a)';

  resposta.getItemResponses().forEach(function (item) {
    const titulo = item.getItem().getTitle().toLowerCase();
    const valor = item.getResponse();
    if (titulo.indexOf('nome') > -1 && valor) nome = valor;
    if (!email && titulo.indexOf('mail') > -1 && valor) email = valor;
  });

  if (!email) return;

  const primeiroNome = String(nome).split(' ')[0];

  // Fallback em texto puro (para clientes que não renderizam HTML)
  const corpoTexto =
    'Olá, ' + primeiroNome + '!\n\n' +
    'Obrigado pelo interesse no Desbravando Rust. Baixe seu capítulo grátis aqui:\n' +
    LINK_CAPITULO + '\n\n' +
    'Boa leitura!\n— José Luis\nhttps://desbravandorust.com.br';

  const corpoHtml = montarHtml(primeiroNome);

  MailApp.sendEmail({
    to: email,
    subject: ASSUNTO,
    body: corpoTexto,
    htmlBody: corpoHtml,
    name: 'José Luis — Desbravando Rust',
  });
}

/**
 * Template do e-mail na identidade visual do projeto (dark + laranja #f74c00).
 * Tabelas + estilos inline para compatibilidade com Gmail/Outlook/Apple Mail.
 */
function montarHtml(primeiroNome) {
  return '' +
  '<body style=\'margin:0;padding:0;background-color:#0e1524;\'>' +
    '<table role=\'presentation\' width=\'100%\' cellpadding=\'0\' cellspacing=\'0\' style=\'background-color:#0e1524;\'>' +
      '<tr><td align=\'center\' style=\'padding:32px 16px;\'>' +
        '<table role=\'presentation\' width=\'600\' cellpadding=\'0\' cellspacing=\'0\' style=\'width:600px;max-width:600px;background-color:#1b2740;border-radius:16px;border-top:4px solid #f74c00;overflow:hidden;\'>' +

          // Marca
          '<tr><td style=\'padding:32px 40px 8px 40px;font-family:Arial,Helvetica,sans-serif;\'>' +
            '<span style=\'font-size:18px;font-weight:bold;color:#e8edf5;\'>Desbravando <span style=\'color:#ff7a3d;\'>Rust</span></span>' +
          '</td></tr>' +

          // Título
          '<tr><td style=\'padding:8px 40px 0 40px;font-family:Arial,Helvetica,sans-serif;\'>' +
            '<h1 style=\'margin:0;font-size:24px;line-height:1.3;color:#e8edf5;\'>Seu capítulo chegou! 🦀</h1>' +
          '</td></tr>' +

          // Corpo
          '<tr><td style=\'padding:20px 40px 0 40px;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.6;color:#b8c2d0;\'>' +
            '<p style=\'margin:0 0 16px 0;\'>Olá, ' + primeiroNome + '!</p>' +
            '<p style=\'margin:0 0 16px 0;\'>Obrigado pelo interesse no <strong style=\'color:#e8edf5;\'>Desbravando Rust</strong>. ' +
            'É o primeiro passo da sua jornada do Python ao Rust — e ela começa agora.</p>' +
          '</td></tr>' +

          // Botão
          '<tr><td align=\'center\' style=\'padding:28px 40px 8px 40px;\'>' +
            '<table role=\'presentation\' cellpadding=\'0\' cellspacing=\'0\'><tr>' +
              '<td align=\'center\' bgcolor=\'#f74c00\' style=\'border-radius:8px;\'>' +
                '<a href=\'' + LINK_CAPITULO + '\' style=\'display:inline-block;padding:14px 32px;font-family:Arial,Helvetica,sans-serif;font-size:16px;font-weight:bold;color:#ffffff;text-decoration:none;border-radius:8px;\'>Baixar o capítulo</a>' +
              '</td>' +
            '</tr></table>' +
          '</td></tr>' +

          // Link alternativo
          '<tr><td align=\'center\' style=\'padding:0 40px 24px 40px;font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:1.5;color:#7d8aa0;\'>' +
            'Se o botão não funcionar, copie este link:<br>' +
            '<a href=\'' + LINK_CAPITULO + '\' style=\'color:#ff7a3d;\'>' + LINK_CAPITULO + '</a>' +
          '</td></tr>' +

          // Rodapé
          '<tr><td style=\'padding:20px 40px 32px 40px;border-top:1px solid #2a3850;font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.6;color:#7d8aa0;\'>' +
            'Boa leitura!<br>José Luis da Cruz Junior · Desbravando Rust<br>' +
            '<a href=\'https://desbravandorust.com.br\' style=\'color:#ff7a3d;text-decoration:none;\'>desbravandorust.com.br</a>' +
          '</td></tr>' +

        '</table>' +
      '</td></tr>' +
    '</table>' +
  '</body>';
}
