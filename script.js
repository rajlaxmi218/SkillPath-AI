const loginForm = document.querySelector('.login-form');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const emailError = document.getElementById('emailError');
const passwordError = document.getElementById('passwordError');

loginForm.addEventListener('submit', function(event) {
  event.preventDefault();

  emailError.textContent = "";
  passwordError.textContent = "";

  let isValid = true;

  if (emailInput.value.trim() === "") {
    emailError.textContent = "Email is required";
    isValid = false;
  }

  if (passwordInput.value.trim() === "") {
    passwordError.textContent = "Password is required";
    isValid = false;
  }else if (passwordInput.value.trim().length < 8) {
    passwordError.textContent = "Password must be at least 8 characters";
    isValid = false;
  }

  if (isValid) {
  console.log("Form is valid! Ready to submit to a server.");
  window.location.href = 'landing.html';
}
});