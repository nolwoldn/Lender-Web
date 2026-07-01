const passwordInput = document.querySelector("#psw");
const passwordCheckBox = document.querySelector("#password-viewr");

passwordCheckBox.addEventListener("click", function () {
  if (passwordInput.type === "password") {
    passwordInput.type = "text";

    this.classList.add("fa-eye-slash");
    this.classList.remove("fa-eye");
  } else {
    passwordInput.type = "password";

    this.classList.remove("fa-eye-slash");
    this.classList.add("fa-eye");
  }
});
