<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import axios from 'axios';

const props = defineProps({
  text: {
    type: String,
    required: true
  },
  articleId: {
    type: [Number, String],
    required: true
  },
  highlights: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['highlight-created', 'highlight-deleted']);

const containerRef = ref(null);
const isSelecting = ref(false);
const renderedHtml = ref(props.text); 

// 하이라이트 목록 감시
watch(() => props.highlights, (newHighlights, oldHighlights) => {
  applyHighlights();
}, { deep: true });

watch(() => props.text, (newText) => {
  renderedHtml.value = newText; 
  applyHighlights(); 
});

// DOM 노드를 순회하며 선택 영역의 실제 텍스트 오프셋 계산 (HTML 태그 무시)
const getTrueCharacterOffset = (container, node, offsetInNode) => {
  let offset = 0;
  const treeWalker = document.createTreeWalker(
    container,
    NodeFilter.SHOW_TEXT, 
    null,
    false
  );

  let currentNode = treeWalker.nextNode();
  while (currentNode) {
    if (currentNode === node) {
      offset += offsetInNode;
      break;
    }
    offset += currentNode.textContent.length;
    currentNode = treeWalker.nextNode();
  }
  return offset;
};

// 텍스트 선택 시작
const handleMouseDown = (e) => {
   // 이제 MARK 클릭 시 선택 방지 로직은 삭제 버튼이 없으므로 필요 없음
   // 마크를 클릭해도 드래그 시작 가능
   isSelecting.value = true;
};

// 텍스트 선택 중
const handleMouseMove = () => {
  if (!isSelecting.value) return;
};

// 텍스트 선택 완료 및 하이라이트 생성 또는 삭제
const handleMouseUp = async () => {
  if (!isSelecting.value) return;
  isSelecting.value = false;

  const selection = window.getSelection();
  if (!selection || !selection.rangeCount || selection.isCollapsed) return;

  const range = selection.getRangeAt(0);
  const container = containerRef.value;
  
  if (!container || !container.contains(range.startContainer) || !container.contains(range.endContainer)) {
      selection.removeAllRanges();
      return;
  }

  const selectedText = range.toString();

    // 선택된 텍스트가 비어있거나 공백만 있는 경우 하이라이트 방지
    if (!selectedText.trim()) {
        selection.removeAllRanges();
        return;
    }

  // 오프셋 계산 로직: DOM 구조와 상관없이 원본 텍스트 기준 오프셋 계산
  // 선택 시작점과 끝점이 원본 텍스트 내 어디에 해당하는지 정확히 찾기
  
  const rangeBeforeStart = document.createRange();
  rangeBeforeStart.setStart(container, 0);
  rangeBeforeStart.setEnd(range.startContainer, range.startOffset);
  const startOffsetBasedOnTextContent = rangeBeforeStart.cloneContents().textContent.length;
  
  const rangeBeforeEnd = document.createRange();
  rangeBeforeEnd.setStart(container, 0);
  rangeBeforeEnd.setEnd(range.endContainer, range.endOffset);
  const endOffsetBasedOnTextContent = rangeBeforeEnd.cloneContents().textContent.length;

  const finalStartOffset = Math.min(startOffsetBasedOnTextContent, endOffsetBasedOnTextContent);
  const finalEndOffset = Math.max(startOffsetBasedOnTextContent, endOffsetBasedOnTextContent);

  const existingHighlight = props.highlights.find(h =>
      h.start_offset === finalStartOffset && h.end_offset === finalEndOffset
  );

  if (existingHighlight) {
      // 동일한 하이라이트가 이미 존재하면 삭제
      console.log(`동일 영역 하이라이트 재선택: 기존 하이라이트 삭제 (ID: ${existingHighlight.id})`);
      deleteHighlight(existingHighlight.id);
  } else {
      // 동일한 하이라이트가 없으면 새로 생성
      console.log(`새로운 영역 하이라이트 선택: 하이라이트 생성`);
      try {
        const response = await axios.post(
          `http://localhost:8000/api/news/${props.articleId}/highlight/`,
          {
            text: selectedText.trim(),
            start_offset: finalStartOffset,
            end_offset: finalEndOffset
          },
          {
            headers: {
              Authorization: `Token ${localStorage.getItem('access')}`
            }
          }
        );

        emit('highlight-created', response.data);

      } catch (error) {
        console.error('하이라이트 생성 실패:', error);
        if (error.response?.status === 401) {
          alert('로그인이 필요한 기능입니다.');
        }
        // 이미 존재하는 하이라이트 에러는 이제 프론트에서 처리하므로 필요 없음

        else {
            alert('하이라이트 생성 중 오류가 발생했습니다.');
        }
      }
  }

  selection.removeAllRanges();
};

// 하이라이트 삭제
const deleteHighlight = async (highlightId) => {
   if (!highlightId) {
       console.error("삭제할 하이라이트 ID가 없습니다.");
       return;
   }

  try {
    await axios.delete(
      `http://localhost:8000/api/news/${highlightId}/delete/`,
      {
        headers: {
          Authorization: `Token ${localStorage.getItem('access')}`
        }
      }
    );
    // 백엔드 삭제 성공 시 이벤트 발생
    emit('highlight-deleted', highlightId);
  } catch (error) {
    console.error('하이라이트 삭제 실패:', error);
     if (error.response?.status === 401) {
       alert('로그인이 필요합니다.');
     } else if (error.response?.status === 404) {
        alert('삭제하려는 하이라이트를 찾을 수 없습니다.');
     } else {
        alert('하이라이트 삭제 중 오류가 발생했습니다.');
     }
  }
};

// 하이라이트 적용 로직 (DOM에 MARK 태그 삽입) - 겹치는 하이라이트 처리 개선
const applyHighlights = () => {
//   console.log('🎨 HighlightableText: applyHighlights 실행');
  if (!props.text || !containerRef.value) {
      console.log('  - 컨테이너 또는 텍스트 없음. applyHighlights 중단.');
      return;
  }
//   console.log('  - 현재 props.highlights:', props.highlights.map(h => h.id));

  const originalText = props.text;
  let html = '';
  
  // 하이라이트 이벤트를 시작/끝 지점 기준으로 모으고 정렬합니다.
  // 각 이벤트는 { offset: number, type: 'start' | 'end', id: highlightId } 형태입니다.
  const highlightEvents = [];
  props.highlights.forEach(h => {
      // 하이라이트 범위가 유효한지 확인
      if (h.start_offset < h.end_offset) {
          highlightEvents.push({ offset: h.start_offset, type: 'start', id: h.id });
          highlightEvents.push({ offset: h.end_offset, type: 'end', id: h.id });
      }
  });

  // 오프셋 기준으로 이벤트를 정렬하되, 동일 오프셋의 경우 'end'가 'start'보다 먼저 오도록 합니다.
  highlightEvents.sort((a, b) => {
      if (a.offset !== b.offset) {
          return a.offset - b.offset;
      } else {
          // 동일 오프셋: 'end'가 먼저 오도록 정렬
          if (a.type === 'end' && b.type === 'start') return -1;
          if (a.type === 'start' && b.type === 'end') return 1;
          return 0; // 동일 타입 또는 기타 경우
      }
  });

  let currentOffset = 0;
  let openHighlights = new Set(); // 현재 열려있는 하이라이트 ID 목록

  highlightEvents.forEach(event => {
      // 이벤트 지점까지의 텍스트 추가
      if (event.offset > currentOffset) {
          html += originalText.slice(currentOffset, event.offset);
      }

      // 이벤트 타입에 따라 열린 하이라이트 목록 업데이트 및 태그 추가/제거
      if (event.type === 'start') {
          // 이전에 열린 하이라이트가 없었다면 <mark> 태그 시작
          if (openHighlights.size === 0) {
              html += '<mark class="highlight">';
          }
          openHighlights.add(event.id);
      } else { // type === 'end'
          openHighlights.delete(event.id);
          // 모든 하이라이트가 닫혔다면 </mark> 태그 닫기
          if (openHighlights.size === 0) {
              html += '</mark>';
          }
      }

      // 현재 오프셋 업데이트
      currentOffset = event.offset;
  });

  // 마지막 이벤트 이후 남은 텍스트 추가
  if (currentOffset < originalText.length) {
      html += originalText.slice(currentOffset);
  }

  // Update the ref holding the rendered HTML
  renderedHtml.value = html;

};

// 컴포넌트 마운트 시 초기 하이라이트 적용 및 이벤트 리스너 추가
onMounted(() => {
  // 초기에 props.highlights 값을 사용하여 하이라이트 적용 (renderedHtml ref 업데이트)
  applyHighlights();

  const container = containerRef.value; // containerRef는 이벤트 리스너용으로 필요
   if (container) {
      container.addEventListener('mouseup', handleMouseUp);
      container.addEventListener('mousedown', handleMouseDown); // Keep mousedown for isSelecting flag
   }
});

// 컴포넌트 언마운트 시 이벤트 리스너 정리
onUnmounted(() => {
  const container = containerRef.value; // containerRef는 이벤트 리스너용으로 필요
  if (container) {
    container.removeEventListener('mouseup', handleMouseUp);
    container.removeEventListener('mousedown', handleMouseDown); // Remove mousedown listener
  }
});

</script>

<template>
  <div
    ref="containerRef"
    class="highlightable-text"
    @mousedown="handleMouseDown"
    @mousemove="handleMouseMove"
    @mouseup="handleMouseUp"
    @mouseleave="isSelecting = false"
    v-html="renderedHtml"
  >
  </div>
</template>

<style scoped>
.highlightable-text {
  position: relative;
  line-height: 1.6;
  white-space: pre-wrap;
  user-select: text;
}

.highlightable-text mark.highlight {
  background-color: #ffd000;
  padding: 2px 0;
  /* position: relative; 삭제 버튼 관련 스타일 제거 */
  cursor: pointer;
}

</style> 