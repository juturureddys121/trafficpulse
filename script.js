const inputEl = document.getElementById('userInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const sampleBtn = document.getElementById('sampleBtn');
const detectedIntentEl = document.getElementById('detectedIntent');
const riskLevelEl = document.getElementById('riskLevel');
const riskScoreEl = document.getElementById('riskScore');
const sourceListEl = document.getElementById('sourceList');
const actionListEl = document.getElementById('actionList');
const timestampEl = document.getElementById('timestamp');

function renderActions(actions) {
  actionListEl.innerHTML = actions
    .map(
      (action, index) => `
        <div class="action-item">
          <div class="action-index">${index + 1}</div>
          <div class="action-text">
            <div class="action-title">${action.title}</div>
            <div class="action-detail">${action.detail}</div>
          </div>
          <div class="action-tag">${action.tag}</div>
        </div>
      `
    )
    .join('');
}

function renderSources(sources) {
  sourceListEl.innerHTML = sources.map((source) => `<li>${source}</li>`).join('');
}

function updateTimestamp() {
  const now = new Date();
  timestampEl.textContent = now.toLocaleTimeString([], {
    hour: 'numeric',
    minute: '2-digit'
  });
}

async function analyzeIntent() {
  const text = inputEl.value.trim();

  if (!text) {
    inputEl.focus();
    return;
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ input: text })
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    detectedIntentEl.textContent = data.intent;
    riskLevelEl.textContent = data.risk_level;
    riskScoreEl.textContent = `${data.risk_score}%`;
    renderSources(data.sources);
    renderActions(data.actions);
    updateTimestamp();
  } catch (error) {
    detectedIntentEl.textContent = 'API unavailable';
    riskLevelEl.textContent = 'Unknown';
    riskScoreEl.textContent = '--';
    renderSources(['Local fallback mode']);
    renderActions([
      {
        title: 'Retry the analysis request',
        detail: 'The app could not reach the local intelligence service. Confirm the server is running and try again.',
        tag: 'Retry'
      }
    ]);
  }
}

analyzeBtn.addEventListener('click', analyzeIntent);

sampleBtn.addEventListener('click', () => {
  inputEl.value = 'Traffic is terrible on the highway, I need to get to the clinic before 9am, and I also need to check if the weather will affect my commute.';
  analyzeIntent();
});

inputEl.addEventListener('keydown', (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    analyzeIntent();
  }
});

analyzeIntent();
