const username = document.querySelector("#username");
const password_input = document.querySelector("#password");
const cpass = document.querySelector("#cpass");
const submit_btn = document.querySelector("#submit");
const show_pass = document.querySelector("#check");
const fail = document.querySelector(".fail");
const validator = /^(?=.*[a-z])(?=.*[0-9])$/;

function show(){
  password_input.type = show_pass.checked ? "text" : "password";
  cpass.type = password_input.type;
}

submit_btn.addEventListener("click", () => {
  if (!(cpass.value === password_input.value)) {
    event.preventDefault();
    show_pass.checked = true;
    show()
    fail.innerText = " Passwords do not match";
    return;
  }
});
show_pass.addEventListener('change',show);
