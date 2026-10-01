/* BioMap Cartago — pestaña Resultados: conclusiones del informe de recomendaciones y descarga del PDF.
   Lee datos/informe/resultados.json, que genera informe/generar.mjs a partir del mismo contenido
   que el PDF: la pestaña y el informe dicen lo mismo. */
'use strict';
(function () {
  const BM = window.BM;
  const { $, esc } = BM;

  const TIPO = { hallazgo: 'Hallazgo', dato: 'Dato', recomendacion: 'Recomendación' };
  const PLAZO_CORTO = (p) => String(p || '').split(' (')[0];

  function cabecera(r) {
    const m = r.meta || {};
    const pdf = r.pdf || {};
    $('#res-cabecera').innerHTML = `
      <div class="res-portada">
        <span class="res-kicker">Informe técnico · ${esc(m.fecha || '')}</span>
        <h2 class="res-titulo">${esc(m.titulo || 'Hallazgos y recomendaciones')}</h2>
        ${m.subtitulo ? `<p class="res-sub">${esc(m.subtitulo)}</p>` : ''}
        <p class="res-dest">Para: ${esc((m.destinatarios || []).join(' · '))}</p>
        ${pdf.archivo ? `<a class="boton res-descarga" href="datos/${esc(pdf.archivo)}?v=${esc(pdf.version || '1')}" download>
          <span aria-hidden="true">⬇</span> Descargar el informe completo
          <small>PDF · ${esc(pdf.paginas || '')} páginas · ${esc(pdf.tamano || '')}</small></a>` : ''}
        <p class="nota">${esc(m.autor || '')} · Normas APA, 7.ª edición · Datos abiertos verificables.</p>
      </div>`;
  }

  function tarjetas(lista) {
    $('#res-tarjetas').innerHTML = (lista || []).map((t) => `
      <article class="tarjeta-res" data-tipo="${esc(t.tipo || 'dato')}">
        <span class="tr-tipo">${esc(TIPO[t.tipo] || 'Dato')}${t.dependencia ? ` · ${esc(t.dependencia)}` : ''}</span>
        <div class="tr-cifra">${esc(t.cifra || '')}${t.unidad ? `<small>${esc(t.unidad)}</small>` : ''}</div>
        <h3 class="tr-titulo">${esc(t.titulo || '')}</h3>
        <p class="tr-frase">${esc(t.frase || '')}</p>
        ${t.fuente ? `<p class="tr-fuente">${esc(t.fuente)}</p>` : ''}
      </article>`).join('');
  }

  function prioridades(lista) {
    $('#res-prioridades').innerHTML = (lista || []).map((p) => `<li>${esc(p)}</li>`).join('');
  }

  function recomendaciones(lista) {
    $('#res-recomendaciones').innerHTML = (lista || []).map((d, i) => `
      <details class="ficha-capa res-dep"${i === 0 ? ' open' : ''}>
        <summary>${esc(d.dependencia)}<small>${d.acciones.length} ${d.acciones.length === 1 ? 'acción' : 'acciones'}</small></summary>
        <ol class="res-acciones">${d.acciones.map((a) => `
          <li>
            <p class="ra-accion">${esc(a.accion)}</p>
            <p class="ra-meta"><span class="chip-p ${a.prioridad === 'alta' ? 'alta' : ''}">Prioridad ${esc(a.prioridad || '')}</span><span class="chip-p">Plazo ${esc(PLAZO_CORTO(a.plazo))}</span>${a.fundamento ? `<span class="chip-p norma" title="${esc(a.fundamento.cita || '')}">${esc({ obligacion: 'Obligación', obligacion_condicionada: 'Obligación condicionada', competencia: 'Competencia' }[a.fundamento.tipo] || 'Orientación técnica')}: ${esc(a.fundamento.norma || '')}${a.fundamento.articulo ? `, ${esc(a.fundamento.articulo)}` : ''}</span>` : ''}</p>
            ${a.dato ? `<p class="ra-dato">${esc(a.dato)}</p>` : ''}
            ${a.zonas ? `<p class="ra-dato">Dónde primero: ${esc(a.zonas)}</p>` : ''}
          </li>`).join('')}
        </ol>
      </details>`).join('');
  }

  /** «Lo que encontramos» en la primera pestaña: los hallazgos del informe en lenguaje claro. */
  function resumenInicio(r) {
    const cont = $('#resumen-hallazgos');
    if (!cont || !(r.hallazgos || []).length) return;
    cont.innerHTML = `<details class="plegable mt-2" open><summary>Lo que encontramos</summary>
      <ul class="hallazgos-claros">${r.hallazgos.map((h) => `<li><b>${esc(h.titulo)}.</b> ${esc(h.tesis)}</li>`).join('')}</ul>
      <button type="button" class="enlace mt-2" data-ir-res>Ver resultados y recomendaciones →</button></details>`;
    $('[data-ir-res]', cont).addEventListener('click', () => BM.irAPestana('tab-res'));
  }

  BM.alIniciar(async () => {
    const r = await BM.leerJSONopcional('informe/resultados.json');
    if (!r) {
      $('#res-cabecera').innerHTML = '<p class="intro">El informe de resultados aún no está publicado.</p>';
      return;
    }
    BM.RESULTADOS = r;
    resumenInicio(r);
    cabecera(r);
    tarjetas(r.tarjetas);
    prioridades(r.prioridades);
    recomendaciones(r.recomendaciones || []);
    $('#res-nota').innerHTML = `${esc(r.aviso || '')} <a href="#" data-ir-met>Método y limitaciones</a>.`;
    $('#res-nota [data-ir-met]').addEventListener('click', (e) => {
      e.preventDefault();
      BM.irAPestana('tab-datos');
      setTimeout(() => $('#metodologia').scrollIntoView({ behavior: 'smooth' }), 80);
    });
  });
})();
