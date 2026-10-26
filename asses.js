/* ================= DATA ================= */
// answer = index of the correct option (0 = first option)
const questionBank = {
  'Web Developer': [
    { q: 'What does HTML stand for?', options: ['Hyper Text Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyperlinks and Text Mark Language'], answer: 0 },
    { q: 'Which CSS property changes the text colour?', options: ['font-style', 'color', 'text-size', 'background'], answer: 1 },
    { q: 'Which tag creates a link?', options: ['<link>', '<a>', '<href>', '<url>'], answer: 1 },
    { q: 'Which language is primarily used to add interactivity to a webpage?', options: ['HTML', 'CSS', 'JavaScript', 'SQL'], answer: 2 },
    { q: 'How do you declare a constant in JavaScript?', options: ['var x', 'let x', 'const x', 'fixed x'], answer: 2 },
    { q: 'What does document.getElementById() return?', options: ['A list of elements', 'One element', 'A string', 'A number'], answer: 1 },
    { q: 'Which method adds an item to the end of an array?', options: ['push()', 'pop()', 'shift()', 'add()'], answer: 0 },
    { q: 'Which CSS layout system arranges items in rows or columns?', options: ['Flexbox', 'Float', 'Table', 'Inline'], answer: 0 },
    { q: 'What does the "===" operator check in JavaScript?', options: ['Only the value', 'Only the type', 'Value and type', 'Nothing'], answer: 2 },
    { q: 'Which HTTP method is normally used to send form data to a server?', options: ['GET', 'POST', 'DELETE', 'HEAD'], answer: 1 }
  ],
  // Used for every career that has no question set yet
  'default': [
    { q: 'What is 15% of 200?', options: ['20', '25', '30', '35'], answer: 2 },
    { q: 'Which is the next number: 2, 4, 8, 16, ...?', options: ['24', '30', '32', '36'], answer: 2 },
    { q: 'What does "debugging" mean?', options: ['Writing new code', 'Finding and fixing errors', 'Deleting files', 'Designing a page'], answer: 1 },
    { q: 'Which of these is a programming language?', options: ['Python', 'Chrome', 'Windows', 'Excel'], answer: 0 },
    { q: 'What does "API" stand for?', options: ['Applied Program Idea', 'Application Programming Interface', 'Automatic Page Input', 'Active Process Index'], answer: 1 },
    { q: 'What does a database store?', options: ['Organised data', 'Only images', 'Only passwords', 'Browser tabs'], answer: 0 },
    { q: 'Which symbol is used for a comment in Python?', options: ['//', '#', '<!-- -->', '**'], answer: 1 },
    { q: 'What does "URL" refer to?', options: ['A web address', 'A programming language', 'A file format', 'A type of virus'], answer: 0 },
    { q: 'What is an algorithm?', options: ['A computer brand', 'Step-by-step instructions to solve a problem', 'A type of cable', 'A website'], answer: 1 },
    { q: 'Which is an example of an operating system?', options: ['Linux', 'Google', 'Python', 'HTML'], answer: 0 }
  ]
};

/* ================= SETUP ================= */
const career = localStorage.getItem('skillpath_career') || 'Web Developer';
const questions = questionBank[career] || questionBank['default'];

const startScreen = document.getElementById('startScreen');
const quizScreen = document.getElementById('quizScreen');
const optionsBox = document.getElementById('options');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

document.getElementById('careerName').textContent = career;

let current = 0;                                   // which question we are on
const answers = new Array(questions.length).fill(null);   // chosen option for each question

/* ================= START ================= */
document.getElementById('takeBtn').addEventListener('click', () => {
  startScreen.hidden = true;
  quizScreen.hidden = false;
  showQuestion();
});

// Complete beginner: no questions. Level = Beginner, then go to the next page.
document.getElementById('beginnerBtn').addEventListener('click', () => {
  localStorage.setItem('skillpath_level', 'Beginner');
  localStorage.setItem('skillpath_route', 'beginner');
  localStorage.setItem('skillpath_score', 0);
  window.location.href = 'result.html';
});

/* ================= QUIZ ================= */
function showQuestion() {
  const item = questions[current];
  const isLast = current === questions.length - 1;

  document.getElementById('counter').textContent = 'Question ' + (current + 1) + ' / ' + questions.length;
  document.getElementById('progressFill').style.width = ((current + 1) / questions.length * 100) + '%';
  document.getElementById('questionText').textContent = item.q;

  prevBtn.disabled = current === 0;                 // no "Previous" on question 1
  nextBtn.textContent = isLast ? 'Finish' : 'Next';
  nextBtn.disabled = answers[current] === null;     // need an answer first

  optionsBox.innerHTML = '';
  item.options.forEach((text, index) => {
    const btn = document.createElement('button');
    btn.className = 'option' + (answers[current] === index ? ' selected' : '');
    btn.textContent = text;
    btn.addEventListener('click', () => {
      answers[current] = index;                      // remember the choice
      document.querySelectorAll('.option').forEach(o => o.classList.remove('selected'));
      btn.classList.add('selected');
      nextBtn.disabled = false;
    });
    optionsBox.appendChild(btn);
  });
}

prevBtn.addEventListener('click', () => {
  if (current > 0) {
    current--;
    showQuestion();
  }
});

nextBtn.addEventListener('click', () => {
  if (current < questions.length - 1) {
    current++;
    showQuestion();
  } else {
    finishQuiz();
  }
});

/* ================= RESULT ================= */
function finishQuiz() {
  // Count correct answers
  let points = 0;
  answers.forEach((choice, i) => {
    if (choice === questions[i].answer) points++;
  });

  // The score is used only to decide the level. It is never shown to the user.
  const percent = Math.round(points / questions.length * 100);
  let level = 'Beginner';
  if (percent >= 75) level = 'Advanced';
  else if (percent >= 40) level = 'Intermediate';

  localStorage.setItem('skillpath_score', points);
  localStorage.setItem('skillpath_level', level);
  localStorage.setItem('skillpath_route', 'assessment');
  window.location.href = 'result.html';
}