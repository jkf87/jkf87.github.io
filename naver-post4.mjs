import puppeteer from 'puppeteer-core';
import { readFileSync } from 'fs';

const bodyHtml = readFileSync('/Users/conanssam-m4/.openclaw/workspace-blogbot/naver_blog_content.html', 'utf-8');
const title = readFileSync('/Users/conanssam-m4/.openclaw/workspace-blogbot/naver_blog_title.txt', 'utf-8').trim();

const browser = await puppeteer.connect({ browserURL: 'http://127.0.0.1:9222' });
// Find the page that has the Naver write editor (in mainFrame)
const allPages = await browser.pages();
let page = null;
let frame = null;
for (const p of allPages) {
  const f = p.frames().find(fr => fr.url().includes('postwrite') || fr.url().includes('PostWriteForm'));
  if (f) { page = p; frame = f; break; }
}
if (!page) { console.error('No editor page found'); process.exit(1); }
console.log('Editor frame URL:', frame.url());

await page.bringToFront();
await new Promise(r => setTimeout(r, 1000));

// First find the title and body elements more carefully
const domInfo = await frame.evaluate(() => {
  // Get all elements with se- classes related to title
  const titleClasses = ['.se-documentTitle', '.se-title', '.se-title-textarea', '.se-title-input'];
  const bodyClasses = ['.se-section-inner', '.se-text-paragraph', '.se-component-content'];
  
  const result = { title: [], body: [] };
  
  for (const cls of titleClasses) {
    const els = document.querySelectorAll(cls);
    els.forEach(el => result.title.push({
      sel: cls,
      tag: el.tagName,
      ce: el.contentEditable,
      cls: el.className?.slice(0, 80),
      text: el.textContent?.slice(0, 30)
    }));
  }
  
  for (const cls of bodyClasses) {
    const els = document.querySelectorAll(cls);
    els.forEach(el => result.body.push({
      sel: cls,
      tag: el.tagName,
      ce: el.contentEditable,
      cls: el.className?.slice(0, 80),
      text: el.textContent?.slice(0, 30)
    }));
  }
  
  // Also get all elements with contenteditable=true or inherit that have reasonable size
  const allCE = document.querySelectorAll('[contenteditable]');
  result.allCE = Array.from(allCE).map(el => ({
    ce: el.contentEditable,
    tag: el.tagName,
    cls: el.className?.slice(0, 80),
    rect: (() => { const r = el.getBoundingClientRect(); return { t: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height) }; })()
  })).filter(e => e.rect.w > 50);
  
  return result;
});
console.log('DOM info:', JSON.stringify(domInfo, null, 2));

// Use CDP to set clipboard - this bypasses focus requirement
console.log('Setting clipboard via CDP...');

// Use IO.stream.write approach or Browser.setClipboard
// Actually, let's use the page to dispatch a custom paste event with our data

// Approach: Inject a paste event handler, then dispatch it with our HTML
console.log('Injecting content via dispatchEvent...');

// First click on the text component to activate it
await frame.evaluate(() => {
  const textComp = document.querySelector('.se-component.se-text');
  if (textComp) textComp.click();
});
await new Promise(r => setTimeout(r, 500));

// Now dispatch a synthetic paste event with HTML data
const insertResult = await frame.evaluate((html) => {
  // Find the active text component's content area
  const content = document.querySelector('.se-component-content') || 
                  document.querySelector('.se-text-paragraph') ||
                  document.querySelector('.se-content');
  
  if (!content) return { error: 'no content area' };
  
  content.focus();
  
  // Create synthetic paste event with HTML
  const clipboardData = new DataTransfer();
  clipboardData.setData('text/html', html);
  clipboardData.setData('text/plain', html);
  
  const pasteEvent = new ClipboardEvent('paste', {
    bubbles: true,
    cancelable: true,
    clipboardData: clipboardData,
  });
  
  content.dispatchEvent(pasteEvent);
  
  return { dispatched: true, target: content.className, targetTag: content.tagName };
}, bodyHtml);

console.log('Paste dispatch result:', JSON.stringify(insertResult));

await new Promise(r => setTimeout(r, 3000));
await page.screenshot({ path: 'paste-dispatch-result.png' });
console.log('Screenshot saved');

browser.disconnect();
