(() => {
  const state = {
    selectedTask: 'clinical_qa',
    debug: false,
  };

  const els = {
    modelInput: document.getElementById('model_input'),
    patientContext: document.getElementById('patient_context'),
    question: document.getElementById('question'),
    structuredOutput: document.getElementById('structured_output'),
    debugRow: document.getElementById('debug_row'),
    showRaw: document.getElementById('show_raw'),
    sendBtn: document.getElementById('send_btn'),
    statusText: document.getElementById('status_text'),
    mainAnswer: document.getElementById('main_answer'),
    copyAnswer: document.getElementById('copy_answer'),
    redFlagsSection: document.getElementById('red_flags_section'),
    redFlags: document.getElementById('red_flags'),
    missingDataSection: document.getElementById('missing_data_section'),
    missingData: document.getElementById('missing_data'),
    nextStepsSection: document.getElementById('next_steps_section'),
    nextSteps: document.getElementById('next_steps'),
    usage: document.getElementById('usage'),
    rawSection: document.getElementById('raw_section'),
    rawJson: document.getElementById('raw_json'),
    taskButtons: document.querySelectorAll('.task-btn'),
  };

  function setStatus(message, isError = false) {
    els.statusText.textContent = message;
    els.statusText.classList.toggle('error', isError);
  }

  function formatValue(value) {
    if (Array.isArray(value)) {
      return value.map((item) => `• ${item}`).join('\n');
    }
    if (value && typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    return value || '';
  }

  function toggleSection(section, contentEl, value) {
    const hasValue = !!(value && (Array.isArray(value) ? value.length : String(value).trim()));
    section.classList.toggle('hidden', !hasValue);
    if (hasValue) contentEl.textContent = formatValue(value);
  }

  function saveLocal() {
    localStorage.setItem('clinical_patient_context', els.patientContext.value);
    localStorage.setItem('clinical_question', els.question.value);
  }

  function loadLocal() {
    els.patientContext.value = localStorage.getItem('clinical_patient_context') || '';
    els.question.value = localStorage.getItem('clinical_question') || '';
  }

  async function loadConfig() {
    try {
      const resp = await fetch('/api/clinical/config/');
      const cfg = await resp.json();
      state.debug = Boolean(cfg.DEBUG);
      els.modelInput.value = cfg.default_model || cfg.model || '';
      els.debugRow.classList.toggle('hidden', !state.debug);
      setStatus('تنظیمات بارگذاری شد.');
    } catch (err) {
      setStatus('خطا در بارگذاری تنظیمات.', true);
    }
  }

  async function askClinical() {
    saveLocal();
    els.sendBtn.disabled = true;
    setStatus('در حال ارسال...');
    els.mainAnswer.textContent = 'در حال دریافت پاسخ...';
    els.usage.textContent = '';
    els.rawJson.textContent = '';
    els.rawSection.classList.add('hidden');
    els.redFlagsSection.classList.add('hidden');
    els.missingDataSection.classList.add('hidden');
    els.nextStepsSection.classList.add('hidden');

    try {
      const payload = {
        task_type: state.selectedTask,
        patient_context: els.patientContext.value,
        question: els.question.value,
        model_input: els.modelInput.value,
        structured_output: els.structuredOutput.checked,
      };

      const resp = await fetch('/api/clinical/ask/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();

      if (!resp.ok) {
        throw new Error(data.detail || 'خطا در دریافت پاسخ');
      }

      const mainText = data.extracted_content || data.answer || 'پاسخی دریافت نشد.';
      els.mainAnswer.textContent = mainText;

      const structured = data.structured_output || {};
      toggleSection(els.redFlagsSection, els.redFlags, structured.red_flags);
      toggleSection(els.missingDataSection, els.missingData, structured.missing_data);
      toggleSection(els.nextStepsSection, els.nextSteps, structured.suggested_next_steps);

      els.usage.textContent = formatValue(data.usage || '');

      if (state.debug && els.showRaw.checked) {
        els.rawSection.classList.remove('hidden');
        els.rawJson.textContent = JSON.stringify(data, null, 2);
      }

      setStatus('پاسخ دریافت شد.');
    } catch (err) {
      els.mainAnswer.textContent = '';
      setStatus(err.message || 'خطای ناشناخته', true);
    } finally {
      els.sendBtn.disabled = false;
    }
  }

  function setupTasks() {
    els.taskButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        state.selectedTask = btn.dataset.task;
        els.taskButtons.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  }

  function setupCopy() {
    els.copyAnswer.addEventListener('click', async () => {
      if (!els.mainAnswer.textContent.trim()) return;
      try {
        await navigator.clipboard.writeText(els.mainAnswer.textContent);
        setStatus('پاسخ کپی شد.');
      } catch {
        setStatus('کپی ناموفق بود.', true);
      }
    });
  }

  function init() {
    loadLocal();
    setupTasks();
    setupCopy();
    els.patientContext.addEventListener('input', saveLocal);
    els.question.addEventListener('input', saveLocal);
    els.sendBtn.addEventListener('click', askClinical);
    loadConfig();
  }

  init();
})();
