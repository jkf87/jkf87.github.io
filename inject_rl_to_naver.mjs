import puppeteer from 'puppeteer-core';
import { readFileSync } from 'fs';

const title = readFileSync('naver_rl_title.txt', 'utf8').trim();
const body = readFileSync('naver_rl_body.txt', 'utf8');
const browser = await puppeteer.connect({ browserURL: 'http://127.0.0.1:9222' });
const pages = await browser.pages();
let page = null;
for (const p of pages) {
  const u = p.url();
  if (u.includes('blog.naver.com') && (u.includes('Redirect=Write') || u.includes('PostWriteForm') || p.frames().some(f => f.url().includes('PostWriteForm') || f.url().includes('postwrite')))) {
    page = p; break;
  }
}
if (!page) throw new Error('Naver write page not found');
await page.bringToFront();
await new Promise(r => setTimeout(r, 1500));

const result = await page.evaluate(({title, body}) => {
  const frame = document.querySelector('iframe#mainFrame');
  const w = frame?.contentWindow || window;
  const ed = w.SmartEditor?._editors?.blogpc001;
  if (!ed) return { error: 'SmartEditor instance not found', href: location.href, frames: [...document.querySelectorAll('iframe')].map(f => f.src) };
  const data = ed.getDocumentData();
  const uuid = () => 'SE-' + crypto.randomUUID();
  const cleanText = (v) => String(v ?? '').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '').trim();
  const para = (value) => ({ id: uuid(), nodes: [{ id: uuid(), value: cleanText(value), '@ctype': 'textNode' }], '@ctype': 'paragraph' });
  const titleComp = data.document.components.find(c => c['@ctype'] === 'documentTitle') || { '@ctype': 'documentTitle' };
  titleComp.title = [para(title)];
  const paragraphs = body.split(/\n\n+/).map(s => s.trim()).filter(Boolean);
  const textComp = { id: uuid(), layout: 'default', value: paragraphs.map(para), '@ctype': 'text' };
  data.document.components = [titleComp, textComp];
  ed.setDocumentData(data);
  return {
    title: ed.getDocumentTitle(),
    textLen: ed.getContentText().length,
    compTypes: ed.getDocumentData().document.components.map(c => c['@ctype']),
    start: ed.getContentText().slice(0, 80),
    hasCodeFence: ed.getContentText().includes('```python') || ed.getContentText().includes('```text')
  };
}, {title, body});
console.log(JSON.stringify(result, null, 2));
await page.screenshot({ path: 'rl-injected.png', fullPage: false });
await browser.disconnect();
