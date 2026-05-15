import puppeteer from 'puppeteer-core';
import { readFileSync } from 'fs';

const bodyHtml = readFileSync('/Users/conanssam-m4/.openclaw/workspace-blogbot/naver_blog_content.html', 'utf-8');
const title = readFileSync('/Users/conanssam-m4/.openclaw/workspace-blogbot/naver_blog_title.txt', 'utf-8').trim();

console.log(`Title: ${title}`);

const browser = await puppeteer.connect({ browserURL: 'http://127.0.0.1:9222' });
const page = (await browser.pages())[0];

// Fill title - find the title contenteditable div
console.log('Finding title element...');
const titleFound = await page.evaluate((t) => {
  // SmartEditor ONE title is usually a contenteditable div with specific class or structure
  // Try multiple selectors
  const selectors = [
    '.se-title-textarea',
    '.se-documentTitle-inputArea',
    '[data-testid="editor-title"]',
    'h1[contenteditable]',
    '.se-title'
  ];
  
  for (const sel of selectors) {
    const el = document.querySelector(sel);
    if (el) {
      el.focus();
      el.textContent = t;
      // Trigger input event so SE picks it up
      el.dispatchEvent(new Event('input', { bubbles: true }));
      return `Found: ${sel}`;
    }
  }
  
  // Fallback: find the first contenteditable that looks like a title area
  const allCE = Array.from(document.querySelectorAll('[contenteditable="true"]'));
  for (const el of allCE) {
    const rect = el.getBoundingClientRect();
    const cls = el.className || '';
    // Title area is usually near the top and has documentTitle in class
    if (cls.includes('title') || cls.includes('Title') || (rect.top < 300 && rect.height < 100 && rect.width > 500)) {
      el.focus();
      el.textContent = t;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      return `Found by heuristic: ${el.className}`;
    }
  }
  
  return 'NOT FOUND';
}, title);
console.log('Title:', titleFound);

await new Promise(r => setTimeout(r, 1000));

// Now fill body - use insertHTML approach
console.log('Filling body...');

// First click the body editor area
const bodyResult = await page.evaluate((html) => {
  // Find body editor - it's the main contenteditable in the editor area
  const allCE = Array.from(document.querySelectorAll('[contenteditable="true"]'));
  
  // The body editor should be the largest contenteditable
  let editor = null;
  let maxArea = 0;
  for (const el of allCE) {
    const rect = el.getBoundingClientRect();
    const area = rect.width * rect.height;
    const cls = el.className || '';
    // Skip title area
    if (cls.includes('title') || cls.includes('Title')) continue;
    if (area > maxArea) {
      maxArea = area;
      editor = el;
    }
  }
  
  if (!editor) return { error: 'no body editor found', ceCount: allCE.length };
  
  editor.focus();
  
  // Use insertHTML to paste the content
  document.execCommand('insertHTML', false, html);
  
  return { success: true, editorClass: editor.className?.slice(0, 60), area: maxArea };
}, bodyHtml);

console.log('Body result:', JSON.stringify(bodyResult));

await new Promise(r => setTimeout(r, 3000));
await page.screenshot({ path: 'final-result.png' });
console.log('Final screenshot saved');

// Disconnect without closing browser
browser.disconnect();
console.log('Done!');
