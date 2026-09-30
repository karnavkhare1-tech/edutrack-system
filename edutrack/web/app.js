/* ════════════════════════════════════════
   EduTrack — app.js
   All UI logic and API communication
   ════════════════════════════════════════ */

const API = {
  get: (url) => fetch(url).then(r => r.json()),
  post: (url, data) => fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
  put: (url, data) => fetch(url, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(r => r.json()),
  del: (url) => fetch(url, { method: 'DELETE' }).then(r => r.json()),
};

// ── State ──
let state = {
  overview: null,
  students: [],
  courses: [],
};

// ── Toast notifications ──
function toast(msg, type = 'info') {
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

// ── Navigation ──
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    item.classList.add('active');
    const page = item.dataset.page;
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById('page-' + page).classList.add('active');
    if (page === 'students') loadStudentsPage();
    if (page === 'courses') loadCoursesPage();
    if (page === 'analytics') loadAnalyticsPage();
    if (page === 'attendance') loadSessionCourseSelect();
  });
});

// ── Modal helpers ──
function openModal(id) {
  document.getElementById(id).classList.remove('hidden');
}
function closeModal(id) {
  document.getElementById(id).classList.add('hidden');
}
document.querySelectorAll('.modal-close').forEach(btn => {
  btn.addEventListener('click', () => closeModal(btn.dataset.modal));
});
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeModal(overlay.id);
  });
});

// ════════════════════════════════════════
// DASHBOARD
// ════════════════════════════════════════
async function loadDashboard() {
  try {
    const data = await API.get('/api/overview');
    if (!data.success) { toast('Failed to load dashboard', 'error'); return; }
    state.overview = data;

    // Badges
    document.getElementById('stat-students').textContent = data.stats.total_students;
    document.getElementById('stat-courses').textContent = data.stats.total_courses;
    document.getElementById('stat-gpa').textContent = data.stats.average_gpa.toFixed(2);
    document.getElementById('stat-debarred').textContent = data.stats.debarred_count;
    document.getElementById('app-version').textContent = `v${data.version}`;

    // Leaderboard
    const lb = document.getElementById('leaderboard-list');
    if (!data.leaderboard.length) {
      lb.innerHTML = '<div class="empty-state">No students yet</div>';
    } else {
      const medals = ['🥇','🥈','🥉'];
      lb.innerHTML = data.leaderboard.map((s, i) => `
        <div class="leader-row">
          <div class="leader-rank">${medals[i] || '#' + (i + 1)}</div>
          <div class="leader-info">
            <div class="leader-name">${esc(s.name)}</div>
            <div class="leader-reg">${esc(s.reg_no)} · ${esc(s.branch)}</div>
          </div>
          <div class="leader-gpa">${s.gpa.toFixed(2)}</div>
        </div>`).join('');
    }

    // Debarred
    const dl = document.getElementById('debarred-list');
    if (!data.debarred.length) {
      dl.innerHTML = '<div class="empty-state">✅ No debarred students</div>';
    } else {
      dl.innerHTML = data.debarred.map(d => `
        <div class="debarred-row">
          <div class="debarred-name">${esc(d.name)} (${esc(d.reg_no)})</div>
          <div>${esc(d.course_code)} — ${d.attended}/${d.total} (${d.percentage}%)</div>
          <div class="debarred-advice">↳ ${esc(d.advice)}</div>
        </div>`).join('');
    }

    state.students = data.students;
    state.courses = data.courses;
  } catch (e) {
    toast('Server not reachable', 'error');
    console.error(e);
  }
}

// ════════════════════════════════════════
// STUDENTS
// ════════════════════════════════════════
async function loadStudentsPage() {
  try {
    const data = await API.get('/api/students');
    if (!data.success) return;
    state.students = data.students;
    renderStudentsTable(data.students);
  } catch(e) { toast('Error loading students', 'error'); }
}

function renderStudentsTable(students) {
  const tbody = document.getElementById('students-tbody');
  if (!students.length) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:1.5rem">No students registered</td></tr>';
    return;
  }
  tbody.innerHTML = students.map(s => {
    const gpaColor = s.gpa >= 8 ? 'var(--accent-green)' : s.gpa >= 6 ? 'var(--accent-yellow)' : 'var(--accent-red)';
    return `
      <tr>
        <td><code>${esc(s.reg_no)}</code></td>
        <td><strong>${esc(s.name)}</strong></td>
        <td><span class="badge badge-blue">${esc(s.branch)}</span></td>
        <td>${s.semester}</td>
        <td style="color:var(--muted);font-size:0.82rem">${esc(s.email)}</td>
        <td><span style="font-weight:700;color:${gpaColor}">${s.gpa.toFixed(2)}</span></td>
        <td>
          <div class="table-actions">
            <button class="btn btn-secondary btn-sm btn-icon" onclick="editStudentModal('${esc(s.reg_no)}')" title="Edit">✎</button>
            <button class="btn btn-danger btn-sm btn-icon" onclick="deleteStudent('${esc(s.reg_no)}')" title="Delete">🗑</button>
          </div>
        </td>
      </tr>`;
  }).join('');
}

// Search
document.getElementById('student-search').addEventListener('input', function() {
  const q = this.value.trim().toLowerCase();
  const filtered = state.students.filter(s =>
    s.name.toLowerCase().includes(q) || s.reg_no.toLowerCase().includes(q)
  );
  renderStudentsTable(filtered);
});

// Add Student
document.getElementById('open-add-student-btn').addEventListener('click', () => openModal('modal-add-student'));
document.getElementById('add-student-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const body = {
    reg_no: document.getElementById('ns-reg').value.trim(),
    name: document.getElementById('ns-name').value.trim(),
    email: document.getElementById('ns-email').value.trim(),
    branch: document.getElementById('ns-branch').value.trim(),
    semester: parseInt(document.getElementById('ns-semester').value),
    phone: document.getElementById('ns-phone').value.trim(),
  };
  const res = await API.post('/api/students', body);
  if (res.success) {
    toast(`Student ${body.name} registered!`, 'success');
    closeModal('modal-add-student');
    e.target.reset();
    loadStudentsPage();
    loadDashboard();
  } else {
    toast(res.error, 'error');
  }
});

// Edit Student
function editStudentModal(regNo) {
  const s = state.students.find(x => x.reg_no === regNo);
  if (!s) return;
  document.getElementById('es-reg').value = s.reg_no;
  document.getElementById('es-name').value = s.name;
  document.getElementById('es-email').value = s.email;
  document.getElementById('es-branch').value = s.branch;
  document.getElementById('es-semester').value = s.semester;
  document.getElementById('es-phone').value = s.phone || '';
  openModal('modal-edit-student');
}

document.getElementById('edit-student-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const regNo = document.getElementById('es-reg').value;
  const body = {
    name: document.getElementById('es-name').value.trim(),
    email: document.getElementById('es-email').value.trim(),
    branch: document.getElementById('es-branch').value.trim(),
    semester: parseInt(document.getElementById('es-semester').value),
    phone: document.getElementById('es-phone').value.trim(),
  };
  const res = await API.put(`/api/students/${regNo}`, body);
  if (res.success) {
    toast('Student updated!', 'success');
    closeModal('modal-edit-student');
    loadStudentsPage();
    loadDashboard();
  } else {
    toast(res.error, 'error');
  }
});

document.getElementById('enroll-btn').addEventListener('click', async () => {
  const regNo = document.getElementById('es-reg').value;
  const code  = document.getElementById('es-enroll-code').value.trim();
  if (!code) { toast('Enter a course code', 'error'); return; }
  const res = await API.post('/api/enroll', { reg_no: regNo, course_code: code });
  if (res.success) {
    toast(res.message, 'success');
    document.getElementById('es-enroll-code').value = '';
    loadStudentsPage(); loadDashboard();
  } else { toast(res.error, 'error'); }
});

document.getElementById('drop-btn').addEventListener('click', async () => {
  const regNo = document.getElementById('es-reg').value;
  const code  = document.getElementById('es-enroll-code').value.trim();
  if (!code) { toast('Enter a course code', 'error'); return; }
  const res = await API.post('/api/drop', { reg_no: regNo, course_code: code });
  if (res.success) {
    toast(res.message, 'success');
    document.getElementById('es-enroll-code').value = '';
    loadStudentsPage(); loadDashboard();
  } else { toast(res.error, 'error'); }
});

async function deleteStudent(regNo) {
  if (!confirm(`Delete student ${regNo}? This cannot be undone.`)) return;
  const res = await API.del(`/api/students/${regNo}`);
  if (res.success) {
    toast(res.message, 'success');
    loadStudentsPage(); loadDashboard();
  } else { toast(res.error, 'error'); }
}

// ════════════════════════════════════════
// COURSES
// ════════════════════════════════════════
async function loadCoursesPage() {
  try {
    const data = await API.get('/api/courses');
    if (!data.success) return;
    state.courses = data.courses;
    const tbody = document.getElementById('courses-tbody');
    if (!data.courses.length) {
      tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--muted);padding:1.5rem">No courses added</td></tr>';
      return;
    }
    tbody.innerHTML = data.courses.map(c => {
      const pct = Math.round((c.enrolled_count / c.max_capacity) * 100);
      const capColor = pct > 90 ? 'var(--accent-red)' : pct > 70 ? 'var(--accent-yellow)' : 'var(--accent-green)';
      return `
        <tr>
          <td><code>${esc(c.code)}</code></td>
          <td>${esc(c.title)}</td>
          <td><span class="badge badge-purple">${c.credits} cr</span></td>
          <td style="font-size:0.83rem">${esc(c.faculty_name)}</td>
          <td><code style="font-size:0.78rem">${esc(c.slot)}</code></td>
          <td><span style="font-weight:600;color:${capColor}">${c.enrolled_count}</span></td>
          <td>${c.max_capacity}</td>
          <td>
            <button class="btn btn-danger btn-sm btn-icon" onclick="deleteCourse('${esc(c.code)}')" title="Delete">🗑</button>
          </td>
        </tr>`;
    }).join('');
  } catch(e) { toast('Error loading courses', 'error'); }
}

document.getElementById('open-add-course-btn').addEventListener('click', () => openModal('modal-add-course'));
document.getElementById('add-course-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const body = {
    code: document.getElementById('nc-code').value.trim(),
    title: document.getElementById('nc-title').value.trim(),
    credits: parseInt(document.getElementById('nc-credits').value),
    faculty_name: document.getElementById('nc-faculty').value.trim() || 'TBA',
    slot: document.getElementById('nc-slot').value.trim() || 'A1',
    max_capacity: parseInt(document.getElementById('nc-capacity').value) || 60,
  };
  const res = await API.post('/api/courses', body);
  if (res.success) {
    toast(`Course ${body.code} added!`, 'success');
    closeModal('modal-add-course');
    e.target.reset();
    loadCoursesPage(); loadDashboard();
  } else { toast(res.error, 'error'); }
});

async function deleteCourse(code) {
  if (!confirm(`Delete course ${code}? Students will be dropped automatically.`)) return;
  const res = await API.del(`/api/courses/${code}`);
  if (res.success) {
    toast(res.message, 'success');
    loadCoursesPage(); loadDashboard();
  } else { toast(res.error, 'error'); }
}

// ════════════════════════════════════════
// ATTENDANCE
// ════════════════════════════════════════

// Tabs
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    const parent = tab.closest('section') || document.body;
    parent.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const target = tab.dataset.tab;
    parent.querySelectorAll('.tab-pane').forEach(p => {
      p.classList.toggle('hidden', p.id !== target);
      p.classList.toggle('active', p.id === target);
    });
  });
});

// Cumulative attendance form
document.getElementById('attendance-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const body = {
    reg_no: document.getElementById('att-reg').value.trim(),
    course_code: document.getElementById('att-course').value.trim(),
    attended: parseInt(document.getElementById('att-attended').value),
    total: parseInt(document.getElementById('att-total').value),
  };
  const res = await API.post('/api/attendance', body);
  const box = document.getElementById('att-result');
  if (res.success) {
    const r = res.record;
    const cls = r.is_debarred ? 'error' : 'success';
    box.className = `result-box ${cls}`;
    box.innerHTML = `
      <strong>${r.percentage}% Attendance</strong><br/>
      Attended: ${r.attended} / ${r.total}<br/>
      Status: <strong>${r.is_debarred ? '⚠ DEBARRED' : '✅ ELIGIBLE'}</strong><br/>
      ${r.advice}`;
    box.classList.remove('hidden');
    toast('Attendance updated!', 'success');
    loadDashboard();
  } else {
    box.className = 'result-box error';
    box.textContent = res.error;
    box.classList.remove('hidden');
  }
});

// Session roll-call
async function loadSessionCourseSelect() {
  try {
    const data = await API.get('/api/courses');
    const sel = document.getElementById('session-course');
    sel.innerHTML = data.courses.map(c =>
      `<option value="${esc(c.code)}">${esc(c.code)} — ${esc(c.title)}</option>`
    ).join('');
  } catch(e) {}
}

let sessionStudents = [];

document.getElementById('load-session-btn').addEventListener('click', async () => {
  const code = document.getElementById('session-course').value;
  const data = await API.get('/api/courses');
  const course = data.courses.find(c => c.code === code);
  if (!course || !course.enrolled_reg_nos.length) {
    document.getElementById('session-student-list').innerHTML = '<div class="empty-state">No students enrolled in this course</div>';
    document.getElementById('session-submit-wrap').style.display = 'none';
    return;
  }

  sessionStudents = course.enrolled_reg_nos.map(reg => {
    const s = state.students.find(x => x.reg_no === reg) || { reg_no: reg, name: reg };
    return { reg_no: reg, name: s.name, present: false };
  });

  const list = document.getElementById('session-student-list');
  list.innerHTML = sessionStudents.map((s, i) => `
    <div class="session-student" id="sess-${i}" onclick="toggleSessionStudent(${i})">
      <span class="session-check">⬜</span>
      <div>
        <div class="session-name">${esc(s.name)}</div>
        <div class="session-reg">${esc(s.reg_no)}</div>
      </div>
    </div>`).join('');
  document.getElementById('session-submit-wrap').style.display = 'block';
});

window.toggleSessionStudent = function(i) {
  sessionStudents[i].present = !sessionStudents[i].present;
  const el = document.getElementById('sess-' + i);
  el.classList.toggle('present', sessionStudents[i].present);
  el.querySelector('.session-check').textContent = sessionStudents[i].present ? '✅' : '⬜';
};

document.getElementById('submit-session-btn').addEventListener('click', async () => {
  const code = document.getElementById('session-course').value;
  const presentRegNos = sessionStudents.filter(s => s.present).map(s => s.reg_no);
  const res = await API.post('/api/attendance/session', { course_code: code, present_reg_nos: presentRegNos });
  if (res.success) {
    toast(`Session recorded: ${presentRegNos.length} present`, 'success');
    loadDashboard();
  } else { toast(res.error, 'error'); }
});

// Audit
document.getElementById('audit-btn').addEventListener('click', async () => {
  const reg = document.getElementById('audit-reg').value.trim();
  if (!reg) { toast('Enter a registration number', 'error'); return; }
  const res = await API.get(`/api/audit/${reg}`);
  const container = document.getElementById('audit-result');
  if (!res.success) {
    container.innerHTML = `<div class="result-box error">${esc(res.error)}</div>`;
    return;
  }
  if (!res.audit.length) {
    container.innerHTML = '<div class="empty-state">No courses enrolled</div>';
    return;
  }
  container.innerHTML = res.audit.map(a => {
    const cls = a.is_debarred ? 'debarred' : a.percentage < 80 ? 'warning' : 'safe';
    const fillPct = Math.min(a.percentage, 100);
    return `
      <div class="card" style="margin-bottom:0.75rem">
        <div class="card-body">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem">
            <strong>${esc(a.course_code)}</strong>
            <span class="badge ${a.is_debarred ? 'badge-red' : 'badge-green'}">${a.is_debarred ? 'DEBARRED' : 'ELIGIBLE'}</span>
          </div>
          <div class="att-bar-wrap">
            <div class="att-bar"><div class="att-fill ${cls}" style="width:${fillPct}%"></div></div>
            <span class="att-pct">${a.percentage}%</span>
          </div>
          <div style="font-size:0.8rem;color:var(--muted);margin-top:0.5rem">
            ${a.attended}/${a.total} classes attended<br/>
            <em>${esc(a.advice)}</em>
          </div>
        </div>
      </div>`;
  }).join('');
});

// ════════════════════════════════════════
// MARKS & GPA
// ════════════════════════════════════════
document.getElementById('marks-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const body = {
    reg_no: document.getElementById('marks-reg').value.trim(),
    course_code: document.getElementById('marks-course').value.trim(),
    quiz: document.getElementById('marks-quiz').value,
    assignment: document.getElementById('marks-assignment').value,
    midterm: document.getElementById('marks-midterm').value,
    final: document.getElementById('marks-final').value,
  };
  const res = await API.post('/api/marks', body);
  const box = document.getElementById('marks-result');
  if (res.success) {
    const g = res.grade;
    const gradeClass = 'grade-' + (g.charAt(0) || 'F');
    box.className = 'result-box success';
    box.innerHTML = `
      <strong>Marks Saved!</strong><br/>
      Total: <strong>${res.total_score}/100</strong>&nbsp;·&nbsp;
      Grade: <strong class="${gradeClass}">${esc(res.grade)}</strong>&nbsp;·&nbsp;
      Grade Point: <strong>${res.grade_point}</strong>&nbsp;·&nbsp;
      Status: <strong>${esc(res.status)}</strong><br/>
      Updated SGPA: <strong style="color:var(--accent-green)">${res.student_gpa.toFixed(2)}</strong>`;
    box.classList.remove('hidden');
    toast('Marks updated!', 'success');
    loadDashboard();
  } else {
    box.className = 'result-box error';
    box.textContent = res.error;
    box.classList.remove('hidden');
  }
});

document.getElementById('transcript-btn').addEventListener('click', async () => {
  const reg = document.getElementById('transcript-reg').value.trim();
  if (!reg) { toast('Enter a registration number', 'error'); return; }
  const res = await API.get(`/api/transcript/${reg}`);
  const container = document.getElementById('transcript-result');
  if (!res.success) {
    container.innerHTML = `<div class="result-box error">${esc(res.error)}</div>`;
    return;
  }
  const t = res.transcript;
  container.innerHTML = `
    <div class="transcript-header">
      <h3>${esc(t.name)}</h3>
      <p>${esc(t.reg_no)} · ${esc(t.branch)} · Semester ${t.semester} · ${t.total_credits} credits</p>
    </div>
    <div style="overflow-x:auto">
      <table class="table">
        <thead>
          <tr><th>Code</th><th>Title</th><th>Cr</th><th>Total</th><th>Att%</th><th>Grade</th><th>Status</th></tr>
        </thead>
        <tbody>
          ${t.records.map(r => {
            const gc = 'grade-' + (r.grade.charAt(0) || 'F');
            return `<tr>
              <td><code>${esc(r.code)}</code></td>
              <td>${esc(r.title.substring(0,22))}${r.title.length > 22 ? '…' : ''}</td>
              <td>${r.credits}</td>
              <td><strong>${r.total}</strong></td>
              <td>${r.attendance_pct}%</td>
              <td><strong class="${gc}">${esc(r.grade)}</strong></td>
              <td><span class="badge ${r.status === 'PASS' ? 'badge-green' : 'badge-red'}">${r.status}</span></td>
            </tr>`;
          }).join('')}
        </tbody>
      </table>
    </div>
    <div class="transcript-gpa">
      <div class="transcript-gpa-value">${t.gpa.toFixed(2)}</div>
      <div class="transcript-gpa-label">SEMESTER GRADE POINT AVERAGE (SGPA)</div>
    </div>`;
});

// ════════════════════════════════════════
// ANALYTICS
// ════════════════════════════════════════
async function loadAnalyticsPage() {
  // Populate course select
  const data = await API.get('/api/courses');
  const sel = document.getElementById('analytics-course-select');
  sel.innerHTML = (data.courses || []).map(c =>
    `<option value="${esc(c.code)}">${esc(c.code)} — ${esc(c.title)}</option>`
  ).join('');

  // Full leaderboard
  const lb = document.getElementById('full-leaderboard');
  const overview = await API.get('/api/overview');
  const medals = ['🥇','🥈','🥉'];
  lb.innerHTML = (overview.leaderboard || []).map((s, i) => `
    <div class="leader-row">
      <div class="leader-rank">${medals[i] || '#' + (i + 1)}</div>
      <div class="leader-info">
        <div class="leader-name">${esc(s.name)}</div>
        <div class="leader-reg">${esc(s.reg_no)} · ${esc(s.branch)} · ${s.courses_enrolled} course(s)</div>
      </div>
      <div class="leader-gpa">${s.gpa.toFixed(2)}</div>
    </div>`).join('') || '<div class="empty-state">No students yet</div>';
}

document.getElementById('analytics-btn').addEventListener('click', async () => {
  const code = document.getElementById('analytics-course-select').value;
  if (!code) { toast('Select a course', 'error'); return; }
  const res = await API.get(`/api/course-analytics/${code}`);
  const container = document.getElementById('analytics-result');
  if (!res.success) {
    container.innerHTML = `<div class="result-box error">${esc(res.error)}</div>`;
    return;
  }
  const a = res.analytics;
  const dist = a.grade_distribution || {};
  const maxCount = Math.max(1, ...Object.values(dist));

  container.innerHTML = `
    <div class="card">
      <div class="card-header"><h2 class="card-title">${esc(a.course_title || a.course_code)}</h2></div>
      <div class="card-body">
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:1rem;margin-bottom:1.25rem">
          <div>
            <div style="font-size:1.4rem;font-weight:700;color:var(--accent-blue)">${a.enrolled_count}</div>
            <div style="font-size:0.78rem;color:var(--muted)">Students Enrolled</div>
          </div>
          <div>
            <div style="font-size:1.4rem;font-weight:700;color:var(--accent-green)">${a.average_score}</div>
            <div style="font-size:0.78rem;color:var(--muted)">Average Score</div>
          </div>
          <div>
            <div style="font-size:1.4rem;font-weight:700;color:var(--accent-purple)">${a.highest_score}</div>
            <div style="font-size:0.78rem;color:var(--muted)">Highest Score</div>
          </div>
          <div>
            <div style="font-size:1.4rem;font-weight:700;color:var(--accent-red)">${a.lowest_score}</div>
            <div style="font-size:0.78rem;color:var(--muted)">Lowest Score</div>
          </div>
          <div>
            <div style="font-size:1.4rem;font-weight:700;color:var(--accent-yellow)">${a.pass_percentage}%</div>
            <div style="font-size:0.78rem;color:var(--muted)">Pass Rate</div>
          </div>
        </div>
        <h3 style="font-size:0.88rem;color:var(--muted);margin-bottom:0.75rem;text-transform:uppercase;letter-spacing:0.04em">Grade Distribution</h3>
        <div class="grade-dist">
          ${Object.entries(dist).filter(([g, c]) => c > 0).map(([g, c]) => `
            <div class="grade-bar-row">
              <div class="grade-label">${esc(g)}</div>
              <div class="grade-track">
                <div class="grade-fill" style="width:${Math.round((c / maxCount) * 100)}%"></div>
              </div>
              <div class="grade-count">${c}</div>
            </div>`).join('')}
        </div>
      </div>
    </div>`;
});

// ════════════════════════════════════════
// SIDEBAR ACTIONS
// ════════════════════════════════════════
document.getElementById('export-btn').addEventListener('click', async () => {
  const res = await API.post('/api/export', {});
  if (res.success) {
    toast('CSV reports saved to reports/ folder', 'success');
  } else { toast(res.error, 'error'); }
});

document.getElementById('reset-btn').addEventListener('click', async () => {
  if (!confirm('Reset database to sample data? All current entries will be lost!')) return;
  const res = await API.post('/api/reset', {});
  if (res.success) {
    toast('Database reset to seed data', 'success');
    loadDashboard();
  } else { toast(res.error, 'error'); }
});

// ── Utility ──
function esc(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(String(str ?? '')));
  return div.innerHTML;
}

// ── Boot ──
loadDashboard();
