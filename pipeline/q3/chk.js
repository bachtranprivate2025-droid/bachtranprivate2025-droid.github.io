const { chromium } = require('playwright');
(async () => {
  const f = process.argv[2]; const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
  const err = []; p.on('pageerror', e => err.push(e.message)); p.on('console', m => { if (m.type()==='error') err.push(m.text()); });
  await p.goto('file://' + f); await p.waitForTimeout(600);
  const r = await p.evaluate(() => {
    const a = window.reportAudit, R = a.rows;
    const cnt = {}; R.forEach(r => { const g = r.setup && r.setup.grade; cnt[g] = (cnt[g]||0)+1; });
    const ths = [...document.querySelectorAll('th')].map(t=>t.innerText.split('\n')[0]).slice(0,8);
    const ec = document.querySelectorAll('td.earn').length;
    const sum = [...document.querySelectorAll('.setupbox')].map(x=>x.innerText.slice(0,700)).filter(x=>x.startsWith('Mùa BCTC'))[0];
    const dgw = R.find(r=>r.t==='DGW'); const msn = R.find(r=>r.t==='MSN');
    return { cnt, ths, ec, sum, dgw: dgw.setup, msn: msn.setup, A: R.filter(r=>r.setup&&/A/.test(r.setup.grade)).map(r=>r.t+':'+r.setup.grade) };
  });
  await p.selectOption('#sort', 'earnScore'); await p.waitForTimeout(300);
  const top = await p.evaluate(() => [...document.querySelectorAll('tbody tr')].slice(0,8).map(t=>t.querySelector('td').innerText.split('\n')[0]));
  const td = await p.evaluate(() => document.querySelector('td.earn').innerText);
  const sw = await p.evaluate(() => document.documentElement.scrollWidth);
  await p.screenshot({ path: '/tmp/claude-0/-home-claude/a2c511d1-6981-5396-8518-8d161b3b1a1b/scratchpad/earn.png' });
  console.log(JSON.stringify({ err, ...r, top, td, sw }, null, 1)); await b.close();
})();
