import puppeteer from 'puppeteer-core';
import { readFileSync } from 'fs';

const bodyHtml = readFileSync('/Users/conanssam-m4/.openclaw/workspace-blogbot/naver_blog_content.html', 'utf-8');
const title = readFileSync('/Users/conanssam-m4/.openclaw/workspace-blogbot/naver_blog_title.txt', 'utf-8').trim();

console.log(`Title: ${title}`);
console.log(`Body length: ${bodyHtml.length}`);

const browser = await puppeteer.connect({ browserURL: 'http://127.0.0.1:9222' });
const pages = await browser.pages();
const page = pages[0];

// Navigate to write page with blogId
console.log('Navigating to write page...');
await page.goto('https://blog.naver.com/PostWriteForm.naver?blogId=jjoongoo', { waitUntil: 'networkidle2', timeout: 30000 });
console.log('URL:', page.url());

// Wait for editor to load
await new Promise(r => setTimeout(r, 5000));

// Screenshot to see state
await page.screenshot({ path: 'editor-loaded.png' });
console.log('Screenshot saved');

// Find and fill title
const titleEl = await page.$('.se-title-textarea, #title, [data-testid="title"]');
if (titleEl) {
  console.log('Found title element');
  await titleEl.click({ clickCount: 3 });
  await page.keyboard.type(title);
  console.log('Title filled');
} else {
  console.log('Title not found, listing candidates...');
  const inputs = await page.$$eval('textarea, input, [contenteditable]', els => 
    els.slice(0, 20).map(e => ({ tag: e.tagName, id: e.id, cls: e.className?.slice?.(0, 80), ce: e.contentEditable, ph: e.placeholder }))
  );
  console.log(JSON.stringify(inputs, null, 2));
}

// Click on editor body area
const editorEl = await page.$('.se-section-inner, [contenteditable="true"]');
if (!editorEl) {
  console.log('Editor not found');
  await page.screenshot({ path: 'editor-not-found.png' });
  process.exit(1);
}

console.log('Found editor element');
await editorEl.click();
await new Promise(r => setTimeout(r, 500));

// Write HTML to clipboard and paste
// Use CDP to set clipboard and dispatch paste
const cdp = await page.createCDPSession();

// We'll use document.execCommand('insertHTML') approach via evaluate
console.log('Inserting HTML content...');

const result = await page.evaluate((html) => {
  const editor = document.querySelector('.se-section-inner') || 
                 document.querySelector('[contenteditable="true"]');
  if (!editor) return { error: 'no editor' };
  
  // For SmartEditor ONE, we need to use its internal API or simulate paste
  // Try insertHTML via execCommand
  editor.focus();
  document.execCommand('insertHTML', false, html);
  return { success: true };
}, bodyHtml);

console.log('Insert result:', JSON.stringify(result));

await new Promise(r => setTimeout(r, 3000));
await page.screenshot({ path: 'editor-filled.png' });
console.log('Final screenshot saved');

// Don't close - let user review
console.log('Done! Check the browser.');
await new Promise(() => {});
