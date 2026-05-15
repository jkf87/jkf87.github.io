import puppeteer from 'puppeteer-core';
import { readFileSync } from 'fs';

const bodyHtml = readFileSync('naver_blog_content.html', 'utf-8');
const title = readFileSync('naver_blog_title.txt', 'utf-8').trim();

console.log(`Title: ${title}`);
console.log(`Body length: ${bodyHtml.length}`);

const browser = await puppeteer.connect({
  browserURL: 'http://127.0.0.1:9222',
});

const pages = await browser.pages();
const page = pages[0] || await browser.newPage();

// Navigate to Naver blog write page
console.log('Navigating to Naver blog write page...');
await page.goto('https://blog.naver.com/PostWriteForm.naver', { waitUntil: 'networkidle2', timeout: 30000 });

// Check if we need to login
const currentUrl = page.url();
console.log(`Current URL: ${currentUrl}`);

if (currentUrl.includes('login') || currentUrl.includes('Login')) {
  console.log('NEED_LOGIN: Please login in the browser window, then press Enter in the terminal...');
  // For now, just wait for the user to handle login
  await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 120000 }).catch(() => {});
}

// Check again after potential login
const afterLoginUrl = page.url();
console.log(`URL after login check: ${afterLoginUrl}`);

if (!afterLoginUrl.includes('PostWriteForm') && !afterLoginUrl.includes('postwrite')) {
  console.log('Not on write page yet, navigating...');
  await page.goto('https://blog.naver.com/PostWriteForm.naver', { waitUntil: 'networkidle2', timeout: 30000 });
}

// Wait for SmartEditor ONE to load
console.log('Waiting for editor to load...');
await page.waitForSelector('[contenteditable="true"]', { timeout: 20000 }).catch(e => {
  console.log('Contenteditable not found, trying alternative...');
});
await new Promise(r => setTimeout(r, 3000));

// Take screenshot to see state
await page.screenshot({ path: 'naver-editor-state.png' });
console.log('Screenshot saved to naver-editor-state.png');

// Try to find and fill the title
const titleSelectors = ['#title', '.se-title-textarea', 'input[name="title"]'];
let titleFilled = false;
for (const sel of titleSelectors) {
  const el = await page.$(sel);
  if (el) {
    console.log(`Found title element: ${sel}`);
    await el.click({ clickCount: 3 });
    await page.keyboard.type(title);
    titleFilled = true;
    break;
  }
}
if (!titleFilled) {
  console.log('Title element not found. Available elements:');
  const textareas = await page.$$eval('textarea, input[type="text"]', els => els.map(e => ({
    tag: e.tagName,
    id: e.id,
    class: e.className,
    placeholder: e.placeholder
  })));
  console.log(JSON.stringify(textareas, null, 2));
}

// Fill body content via CDP Input.insertText or clipboard
console.log('Filling body content...');

// Approach: Use CDP to dispatch paste event with HTML
// First, click on the editor body area
const editorSelectors = [
  '.se-section-inner',
  '[contenteditable="true"]', 
  '.se-editor-container',
  '#se-editor-container'
];

let editorClicked = false;
for (const sel of editorSelectors) {
  const el = await page.$(sel);
  if (el) {
    console.log(`Found editor element: ${sel}`);
    await el.click();
    editorClicked = true;
    break;
  }
}

if (editorClicked) {
  // Use page.evaluate to inject HTML via clipboard API simulation
  // SmartEditor ONE intercepts paste events, so we need to dispatch a proper paste event
  
  const result = await page.evaluate((html) => {
    // Create a DataTransfer with HTML
    const dt = new DataTransfer();
    const blob = new Blob([html], { type: 'text/html' });
    const file = new File([blob], 'content.html', { type: 'text/html' });
    dt.items.add(file);
    
    // Also add plain text version
    const textBlob = new Blob([html], { type: 'text/plain' });
    const textFile = new File([textBlob], 'content.txt', { type: 'text/plain' });
    dt.items.add(textFile);
    
    // Find the editor container
    const editor = document.querySelector('.se-section-inner') || 
                   document.querySelector('[contenteditable="true"]');
    
    if (!editor) return { error: 'Editor element not found in DOM' };
    
    // Dispatch paste event
    const pasteEvent = new ClipboardEvent('paste', {
      bubbles: true,
      cancelable: true,
      clipboardData: dt,
    });
    
    editor.dispatchEvent(pasteEvent);
    
    return { success: true, editorFound: true, pasteDispatched: true };
  }, bodyHtml);
  
  console.log('Paste result:', JSON.stringify(result));
  
  // Wait for content to render
  await new Promise(r => setTimeout(r, 3000));
}

// Take final screenshot
await page.screenshot({ path: 'naver-editor-final.png' });
console.log('Final screenshot saved to naver-editor-final.png');

// Keep browser open
console.log('\nDone! Browser is still open. Check the editor.');
console.log('The script will keep running. Press Ctrl+C to exit.');

// Don't close browser - keep it open for user to review
await new Promise(() => {});
