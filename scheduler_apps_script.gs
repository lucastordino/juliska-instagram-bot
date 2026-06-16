// ─────────────────────────────────────────────────────────────────────────────
//  PUBLICADOR INSTAGRAM · agendador confiável (Google Apps Script)
//
//  O `schedule` do GitHub Actions (grátis) atrasa horas e às vezes não roda.
//  Este script roda todo dia ~11h BR, vê se há post agendado pro dia, e dispara
//  o workflow do GitHub via API (workflow_dispatch) — que publica na hora.
//
//  SETUP (uma vez):
//   1. Project Settings → fuso horário = (GMT-03:00) São Paulo
//   2. Script Properties → adicionar:  GITHUB_PAT = <token fine-grained do Lucas
//      com permissão "Actions: Read and write" no repo juliska-instagram-bot>
//   3. Rodar a função  criarGatilhoDiario  (autorizar quando pedir) — uma vez
//   4. Rodar  testarToken  pra confirmar o token (não publica nada; espera 200)
// ─────────────────────────────────────────────────────────────────────────────

var REPO = 'lucastordino/juliska-instagram-bot';

// Mapa: data (YYYY-MM-DD, fuso BR) → arquivo do workflow a disparar.
// Fonte única da verdade do horário. Pra adicionar post novo, é só incluir aqui.
var AGENDA = {
  '2026-06-18': 'publicar-dica_a_vista.yml',
  '2026-06-23': 'publicar-campo_belo.yml',
  '2026-06-25': 'publicar-dica_financiamento.yml',
  '2026-06-30': 'publicar-vila_olimpia.yml',
  '2026-07-02': 'publicar-dica_incc.yml',
  '2026-07-07': 'publicar-jardins.yml',
  '2026-07-09': 'publicar-dica_planta_pronto.yml',
  '2026-07-14': 'publicar-pinheiros.yml',
  '2026-07-16': 'publicar-dica_tabela.yml',
  '2026-07-21': 'publicar-vila_nova_conceicao.yml',
  '2026-07-23': 'publicar-dica_permuta.yml',
  '2026-07-28': 'publicar-chacara_sto_antonio.yml',
  '2026-07-30': 'publicar-dica_alem_apartamento.yml'
};

function hojeBR_() {
  return Utilities.formatDate(new Date(), 'America/Sao_Paulo', 'yyyy-MM-dd');
}

// Chamada pelo gatilho diário. Publica o post do dia, se houver.
function publicarPostDoDia() {
  var hoje = hojeBR_();
  var wf = AGENDA[hoje];
  if (!wf) { Logger.log('Sem post agendado para hoje (' + hoje + ').'); return; }
  var code = dispararWorkflow_(wf);
  Logger.log(code === 204 ? ('✅ ' + hoje + ' → ' + wf + ' disparado')
                          : ('❌ ' + hoje + ' → HTTP ' + code));
}

function dispararWorkflow_(arquivo) {
  var token = PropertiesService.getScriptProperties().getProperty('GITHUB_PAT');
  if (!token) { Logger.log('GITHUB_PAT não configurado nas Script Properties.'); return 0; }
  var url = 'https://api.github.com/repos/' + REPO + '/actions/workflows/' + arquivo + '/dispatches';
  var resp = UrlFetchApp.fetch(url, {
    method: 'post',
    headers: {
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    },
    payload: JSON.stringify({ ref: 'main' }),
    muteHttpExceptions: true
  });
  return resp.getResponseCode(); // 204 = sucesso
}

// Testa o token SEM publicar (GET lista os workflows). Espera HTTP 200.
function testarToken() {
  var token = PropertiesService.getScriptProperties().getProperty('GITHUB_PAT');
  var resp = UrlFetchApp.fetch('https://api.github.com/repos/' + REPO + '/actions/workflows', {
    headers: { Authorization: 'Bearer ' + token, Accept: 'application/vnd.github+json' },
    muteHttpExceptions: true
  });
  var c = resp.getResponseCode();
  Logger.log('GET workflows → HTTP ' + c + (c === 200 ? '  ✅ token OK' : '  ❌ ' + resp.getContentText().slice(0, 200)));
}

// Rode UMA vez pra instalar o gatilho diário às 11h (fuso do projeto = SP).
function criarGatilhoDiario() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'publicarPostDoDia') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('publicarPostDoDia').timeBased().everyDays(1).atHour(11).create();
  Logger.log('Gatilho diário criado (~11h, fuso do projeto). Confirme o fuso = São Paulo.');
}
