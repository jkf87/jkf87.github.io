
// 네이버 블로그 자동 포스팅 스크립트

(async function() {
  console.log('자동화 시작...');
  
  // 1. 제목 입력
  const title = 'Claude로 지식 그래프 만들기: 비정형 텍스트에서 엔티티 추출부터 다중 홉 쿼리까지';
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
