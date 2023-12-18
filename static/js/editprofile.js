const aboutInput = document.querySelector('textarea');
setTimeout(() => {
  value = aboutInput.getAttribute('value')
  aboutInput.textContent = value
}, 200)
