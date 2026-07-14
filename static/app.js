const question = document.querySelector('#question');
const askButton = document.querySelector('#ask-button');
const status = document.querySelector('#status');
const result = document.querySelector('#result');
const answer = document.querySelector('#answer');
const gapNote = document.querySelector('#gap-note');
const citationsWrap = document.querySelector('#citations-wrap');
const citations = document.querySelector('#citations');
const groundingBadge = document.querySelector('#grounding-badge');
const charCount = document.querySelector('#char-count');

function updateCount() {
  charCount.textContent = `${question.value.length} / 2000`;
}

function setStatus(message, isError = false) {
  status.textContent = message;
  status.classList.toggle('hidden', !message);
  status.classList.toggle('error', isError);
}

function renderResult(data) {
  result.classList.remove('hidden');
  answer.textContent = data.answer;
  gapNote.textContent = data.gap_note || '';
  gapNote.classList.toggle('hidden', !data.gap_note);
  groundingBadge.textContent = data.grounded ? 'Grounded' : 'Needs review';
  groundingBadge.className = `badge ${data.grounded ? 'success' : 'warning'}`;

  citations.replaceChildren();
  for (const citation of data.citations || []) {
    const item = document.createElement('li');
    const source = document.createElement('strong');
    source.textContent = `${citation.marker} ${citation.source}`;
    const excerpt = document.createElement('span');
    excerpt.textContent = citation.excerpt;
    item.append(source, excerpt);
    citations.append(item);
  }
  citationsWrap.classList.toggle('hidden', !(data.citations || []).length);
}

async function ask() {
  const value = question.value.trim();
  if (!value) {
    setStatus('Enter a question to continue.', true);
    question.focus();
    return;
  }
  document.body.classList.add('is-loading');
  askButton.disabled = true;
  askButton.textContent = 'Researching…';
  result.classList.add('hidden');
  setStatus('Searching your documents and preparing a cited answer…');
  try {
    const response = await fetch('/api/ask', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: value}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The request failed.');
    setStatus('');
    renderResult(data);
  } catch (error) {
    setStatus(error.message || 'The request failed. Please try again.', true);
  } finally {
    document.body.classList.remove('is-loading');
    askButton.disabled = false;
    askButton.innerHTML = 'Ask agent <span aria-hidden="true">→</span>';
  }
}

question.addEventListener('input', updateCount);
question.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') ask();
});
askButton.addEventListener('click', ask);
document.querySelectorAll('.example').forEach((button) => button.addEventListener('click', () => {
  question.value = button.textContent;
  updateCount();
  ask();
}));

updateCount();
