import puppeteer from 'puppeteer-core';
const browser = await puppeteer.connect({ browserURL: 'http://127.0.0.1:9222' });
const pages = await browser.pages();
let page = pages.find(p => p.url().includes('blog.naver.com') && p.url().includes('Redirect=Write')) || pages.find(p => p.url().includes('blog.naver.com'));
await page.bringToFront();
await new Promise(r=>setTimeout(r,3000));
const result = await page.evaluate(() => {
  const w = document.querySelector('iframe#mainFrame')?.contentWindow || window;
  const ed = w.SmartEditor?._editors?.blogpc001;
  if (!ed) return { error: 'no editor' };
  const data = ed.getDocumentData();
  const comps = data.document.components;
  const title = comps.find(c => c['@ctype'] === 'documentTitle');
  const imgs = comps.filter(c => c['@ctype'] === 'image');
  const textComps = comps.filter(c => c['@ctype'] === 'text');
  const uuid = () => 'SE-' + crypto.randomUUID();
  const para = (value) => ({ id: uuid(), nodes: [{ id: uuid(), value, '@ctype': 'textNode' }], '@ctype': 'paragraph' });
  const textComp = (paras) => ({ id: uuid(), layout: 'default', value: paras.map(para), '@ctype': 'text' });
  const paras = textComps.flatMap(tc => (tc.value || [])
    .filter(p => Array.isArray(p?.nodes))
    .map(p => p.nodes.map(n => n?.value || '').join('').trim())
    .filter(Boolean));
  if (imgs.length === 8 && paras.length > 20) {
    const anchors = [
      '### 왜 지금 에이전트인가',
      '핵심은 task horizon',
      '### 훈련 프레임워크',
      '### CodeClash',
      '### 좋은 벤치마크',
      '## 3. Alex Zhang',
      '## 4. Will Brown',
      '## 5. 패널 토론'
    ];
    const positions = anchors.map(a => Math.max(1, paras.findIndex(p => p.includes(a.replace(/^#+\s*/, ''))))).map((x,i)=> x < 0 ? Math.min(paras.length, 3+i*5) : x);
    let out = [title];
    let start = 0;
    for (let i=0; i<imgs.length; i++) {
      const end = Math.max(start, positions[i] ?? paras.length);
      if (end > start) out.push(textComp(paras.slice(start, end)));
      out.push(imgs[i]);
      start = end;
    }
    if (start < paras.length) out.push(textComp(paras.slice(start)));
    data.document.components = out.filter(Boolean);
    ed.setDocumentData(data);
  }
  const d2 = ed.getDocumentData();
  const txt = ed.getContentText();
  return {
    title: ed.getDocumentTitle(),
    textLen: txt.length,
    images: d2.document.components.filter(c => c['@ctype'] === 'image').length,
    order: d2.document.components.map(c => c['@ctype']),
    hasCodeFence: txt.includes('```python') || txt.includes('```text'),
    sampleCode: txt.includes('def ') || txt.includes('import '),
    start: txt.slice(0,100),
    end: txt.slice(-160)
  };
});
console.log(JSON.stringify(result, null, 2));
await page.screenshot({ path: 'rl-after-images.png', fullPage: false });
await browser.disconnect();
