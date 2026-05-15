import puppeteer from 'puppeteer-core';
import { readFileSync } from 'fs';

const title = readFileSync('naver_rl_title.txt', 'utf8').trim();
const raw = readFileSync('naver_rl_body.txt', 'utf8');

function cleanMarkdown(md) {
  const lines = md.split('\n');
  const out = [];
  let inCode = false;
  let codeBuf = [];
  let codeLang = '';
  const flushCode = () => {
    if (!codeBuf.length) return;
    out.push(`【코드${codeLang ? ': ' + codeLang : ''}】`);
    out.push(codeBuf.join('\n'));
    out.push('【/코드】');
    codeBuf = [];
    codeLang = '';
  };
  for (const line of lines) {
    const fence = line.match(/^```\s*([\w+-]*)\s*$/);
    if (fence) {
      if (!inCode) { inCode = true; codeLang = fence[1] || ''; codeBuf = []; }
      else { inCode = false; flushCode(); }
      continue;
    }
    if (inCode) { codeBuf.push(line); continue; }
    let s = line;
    s = s.replace(/^#{1,6}\s+/, '');
    s = s.replace(/^[-*]\s+/, '• ');
    s = s.replace(/^\d+\.\s+/, (m) => m);
    s = s.replace(/\*\*(.*?)\*\*/g, '$1');
    s = s.replace(/`([^`]+)`/g, '$1');
    out.push(s);
  }
  if (inCode) flushCode();
  return out.join('\n').replace(/\n{3,}/g, '\n\n');
}

const body = cleanMarkdown(raw);

const browser = await puppeteer.connect({ browserURL: 'http://127.0.0.1:9222' });
const pages = await browser.pages();
let page = pages.find(p => p.url().includes('Redirect=Update') && p.url().includes('224279163873')) || pages.find(p => p.url().includes('blog.naver.com'));
if (!page) throw new Error('Naver update page not found');
await page.bringToFront();
await new Promise(r => setTimeout(r, 1500));

const result = await page.evaluate(({title, body}) => {
  const frame = document.querySelector('iframe#mainFrame');
  const w = frame?.contentWindow || window;
  const ed = w.SmartEditor?._editors?.blogpc001;
  if (!ed) return { error: 'SmartEditor not found' };
  const data = ed.getDocumentData();
  const existingImages = data.document.components.filter(c => c['@ctype'] === 'image');
  const uuid = () => 'SE-' + crypto.randomUUID();
  const cleanText = (v) => String(v ?? '').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '').trim();
  const para = (value) => ({ id: uuid(), nodes: [{ id: uuid(), value: cleanText(value), '@ctype': 'textNode' }], '@ctype': 'paragraph' });
  const textComp = (paras) => ({ id: uuid(), layout: 'default', value: paras.map(para), '@ctype': 'text' });
  const titleComp = data.document.components.find(c => c['@ctype'] === 'documentTitle') || { '@ctype': 'documentTitle' };
  titleComp.title = [para(title)];
  const paras = body.split(/\n\n+/).map(s => s.trim()).filter(Boolean);
  const anchors = ['왜 지금 에이전트인가', '핵심은 task horizon', '훈련 프레임워크', 'CodeClash', '좋은 벤치마크', '3. Alex Zhang', '4. Will Brown', '5. 패널 토론'];
  const positions = anchors.map((a,i) => {
    const idx = paras.findIndex(p => p.includes(a));
    return idx < 0 ? Math.min(paras.length, 3 + i * 5) : idx;
  });
  let comps = [titleComp];
  let start = 0;
  for (let i = 0; i < existingImages.length; i++) {
    const end = Math.max(start, positions[i] ?? paras.length);
    if (end > start) comps.push(textComp(paras.slice(start, end)));
    comps.push(existingImages[i]);
    start = end;
  }
  if (start < paras.length) comps.push(textComp(paras.slice(start)));
  data.document.components = comps.filter(Boolean);
  ed.setDocumentData(data);
  const txt = ed.getContentText();
  return {
    title: ed.getDocumentTitle(),
    textLen: txt.length,
    images: ed.getDocumentData().document.components.filter(c => c['@ctype'] === 'image').length,
    hasMarkdownHeading: /(^|\n)#{1,6}\s/.test(txt),
    hasFence: txt.includes('```'),
    hasCodeMarkers: txt.includes('【코드: python】'),
    sample: txt.slice(txt.indexOf('코드'), txt.indexOf('코드') + 200)
  };
}, {title, body});
console.log(JSON.stringify(result, null, 2));
await page.screenshot({ path: 'rl-fixed-markdown.png', fullPage: false });
await browser.disconnect();
