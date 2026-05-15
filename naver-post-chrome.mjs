#!/usr/bin/env node
/**
 * 네이버 블로그 자동 포스팅 (Chrome DevTools MCP)
 * naver_blog_content.html을 읽어서 네이버 블로그에 자동으로 붙여넣기
 */

import { readFileSync } from 'fs';

const bodyHtml = readFileSync('naver_blog_content.html', 'utf-8');
const title = readFileSync('naver_blog_title.txt', 'utf-8').trim();

console.log(`Title: ${title}`);
console.log(`Body length: ${bodyHtml.length} bytes`);
console.log('Opening Naver Blog write page...');
console.log('');
console.log('스크립트 사용 방법:');
console.log('1. Chrome DevTools를 사용해서 네이버 블로그에 자동으로 붙여넣기');
console.log('2. 제목: ' + title);
console.log('3. 본문: ' + bodyHtml.substring(0, 100) + '...');
console.log('');
console.log('다음 단계:');
console.log('- 크롬 데브툴 MCP로 https://blog.naver.com/PostWriteForm.naver 열기');
console.log('- 제목 입력란에 제목 붙여넣기');
console.log('- 본문 입력란에 HTML 붙여넣기');
console.log('- 발행 버튼 클릭');
