const level = localStorage.getItem('skillpath_level');
const route = localStorage.getItem('skillpath_route');   // 'assessment' or 'beginner'

// Nothing saved yet? Send the user to the assessment first.
if (!level) {
  window.location.href = 'assessment.html';
}

// The numeric score stays in localStorage for internal use. It is never shown.
const messages = {
  'Beginner': 'You are at the start of your journey. We will build up from the basics.',
  'Intermediate': 'You have a good understanding of the fundamentals.',
  'Advanced': 'You have a strong command of the fundamentals.'
};

if (route === 'beginner') {
  document.getElementById('beginnerView').hidden = false;
} else {
  document.getElementById('levelName').textContent = level;
  document.getElementById('levelMessage').textContent = messages[level];
  document.getElementById('assessedView').hidden = false;
}