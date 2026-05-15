#!/usr/bin/env node
/**
 * 네이버 블로그 자동 포스팅 (Chrome DevTools)
 * HTML과 제목을 읽어서 네이버 블로그에 자동으로 입력 및 발행
 */

import { readFileSync, writeFileSync } from 'fs';

const title = readFileSync('naver_blog_title.txt', 'utf-8').trim();
const bodyHtml = readFileSync('naver_blog_content.html', 'utf-8');

console.log('='.repeat(60));
console.log('네이버 블로그 자동 포스팅 준비 완료');
console.log('='.repeat(60));
console.log('');
console.log('📝 제목:');
console.log(title);
console.log('');
console.log('📄 본문 크기: ' + (bodyHtml.length / 1024).toFixed(2) + ' KB');
console.log('');
console.log('다음 단계:');
console.log('1. Chrome DevTools를 사용해서 다음 작업 자동화:');
console.log('   - 제목 입력란에 제목 입력');
console.log('   - SmartEditor에 HTML 붙여넣기');
console.log('   - 발행 버튼 클릭');
console.log('');
console.log('2. 또는 수동으로:');
console.log('   - 제목: 복사해서 붙여넣기');
console.log('   - 본문: naver_blog_content.html의 HTML 복사 후 Ctrl+V');
console.log('   - 발행 클릭');
console.log('');
console.log('='.repeat(60));

// 자동화 스크립트 작성
const automationScript = `
// 네이버 블로그 자동 포스팅 스크립트

(async function() {
  console.log('자동화 시작...');
  
  // 1. 제목 입력
  const title = '${title.replace(/'/g, "\\'")}';
  const titleInputs = document.querySelectorAll('input[type="text"], textarea');
  let titleSet = false;
  
  for (const input of titleInputs) {
    if (input.offsetParent !== null) { // 보이는 요소만
      input.value = title;
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
      titleSet = true;
      console.log('✓ 제목 입력됨');
      break;
    }
  }
  
  if (!titleSet) console.log('⚠ 제목 입력 필드를 찾을 수 없음');
  
  // 2. SmartEditor iframe 찾기
  const editorIframes = document.querySelectorAll('iframe');
  console.log('발견된 iframe: ' + editorIframes.length + '개');
  
  // 3. 잠시 대기 후 본문 클릭
  await new Promise(r => setTimeout(r, 1000));
  
  // 본문 영역 클릭
  const editorArea = document.querySelector('[contenteditable], .se-section-inner, .se-editor-container');
  if (editorArea) {
    editorArea.click();
    console.log('✓ 에디터 영역 클릭됨');
  }
  
  console.log('자동화 완료');
  console.log('이제 본문을 붙여넣기할 준비가 되었습니다.');
})();
`;

writeFileSync('/Users/conanssam-m4/.openclaw/workspace-blogbot/naver-automation.js', automationScript);

console.log('✅ 자동화 스크립트 생성됨: naver-automation.js');
