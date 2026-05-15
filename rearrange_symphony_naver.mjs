import puppeteer from 'puppeteer-core';
const browser = await puppeteer.connect({ browserURL:'http://127.0.0.1:9222' });
const pages = await browser.pages();
let page = pages.find(p => p.url().includes('blog.naver.com') && p.url().includes('Redirect=Write'));
await page.bringToFront();
await new Promise(r=>setTimeout(r,2500));
const result = await page.evaluate(() => {
  const w = document.querySelector('iframe#mainFrame')?.contentWindow || window;
  const ed = w.SmartEditor?._editors?.blogpc001;
  if (!ed) return {error:'no editor'};
  const data = ed.getDocumentData();
  const title = data.document.components.find(c=>c['@ctype']==='documentTitle');
  const imgs = data.document.components.filter(c=>c['@ctype']==='image');
  const paras = data.document.components.filter(c=>c['@ctype']==='text').flatMap(tc => (tc.value||[]).map(p => (p.nodes||[]).map(n=>n.value||'').join('').trim()).filter(Boolean));
  const uuid = ()=>'SE-'+crypto.randomUUID();
  const para = value => ({id:uuid(), nodes:[{id:uuid(), value, '@ctype':'textNode'}], '@ctype':'paragraph'});
  const textComp = ps => ({id:uuid(), layout:'default', value:ps.map(para), '@ctype':'text'});
  if (imgs.length) {
    const anchors = ['1. 왜 Symphony가 나왔나','3. 이슈 트래커가 컨트롤 플레인이 된다','7. 참조 구현은 Elixir다'];
    const positions = anchors.map((a,i)=>{ const idx=paras.findIndex(p=>p.includes(a)); return idx<0?Math.min(paras.length, 2+i*15):idx; });
    let out=[title], start=0;
    for (let i=0;i<imgs.length;i++) {
      const end=Math.max(start, positions[i] ?? paras.length);
      if (end>start) out.push(textComp(paras.slice(start,end)));
      out.push(imgs[i]);
      start=end;
    }
    if (start<paras.length) out.push(textComp(paras.slice(start)));
    data.document.components = out.filter(Boolean);
    ed.setDocumentData(data);
  }
  const txt=ed.getContentText();
  return {title:ed.getDocumentTitle(), images:ed.getDocumentData().document.components.filter(c=>c['@ctype']==='image').length, order:ed.getDocumentData().document.components.map(c=>c['@ctype']), textLen:txt.length, hasMarkdownHeading:/(^|\n)#{1,6}\s/.test(txt), hasFence:txt.includes('```'), hasCodeMarker:txt.includes('【코드'), hasSource:txt.includes('https://github.com/openai/symphony')};
});
console.log(JSON.stringify(result,null,2));
await page.screenshot({path:'symphony-after-images.png', fullPage:false});
await browser.disconnect();
